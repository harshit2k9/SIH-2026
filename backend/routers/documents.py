"""
POST /documents/upload

Flow (mirrors the design confirmed with the team):
  1. Rate limit (per-user, via slowapi)
  2. JWT auth
  3. RBAC: case upload permission
  4. Pre-flight Content-Length check
  5. Streaming write to quarantine dir, 1MB chunks, incremental SHA-256
  6. Magic-byte MIME validation
  7. ClamAV scan
  8. Move to MinIO (encrypted, bucket-versioned)
  9. Single DB transaction: insert document row + document_version row + hash-chained audit entry
  10. Return minimal metadata (never expose internal storage path)

Every failure path cleans up the quarantine file and (if applicable) the
uploaded MinIO object, and logs a security event without leaking internal
details to the client.

SCHEMA NOTES (Production):
- documents table: metadata only (case_id, title, document_type, confidentiality_level, current_version, etc.)
- document_versions table: file storage details (version_number, storage_uri, sha256_checksum, file_size_bytes, etc.)
- All IDs are UUIDs, not integers
- document_versions has unique constraint on (document_id, version_number)
"""
import logging
import traceback
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status, Query
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings
from database import get_pool
from schemas import (
    DocumentUploadResponse,
    PaginatedDocumentsResponse,
    DocumentDownloadResponse,
    DocumentResponse,
    AuditLogResponse,
    DocumentMetadataUpdate,
    ShareDocumentRequest,
)
from security.auth import AuthenticatedUser, verify_jwt
from security.rbac import require_upload_permission
from security.sanitize import assert_allowed_mime, detect_true_mime, extension_for_mime, sanitize_display_filename
from services.storage import upload_file, delete_object, generate_presigned_download_url
from services.antivirus import scan_file
from services.audit import write_audit_entry, log_audit_event

import asyncpg

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security_events")
limiter = Limiter(key_func=get_remote_address)

Path(settings.QUARANTINE_DIR).mkdir(parents=True, exist_ok=True)

# Dedicated error log file — guarantees the full traceback lands somewhere
ERROR_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "upload_errors.log"

ALLOWED_DOC_TYPES = {"FIR", "ChargeSheet", "Evidence", "Forensic Report", "Witness Statement", "Legal Notice", "Judgment", "Other"}

def _log_full_traceback(context: str) -> None:
    tb_text = traceback.format_exc()
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*80}\n{context}\n{'='*80}\n{tb_text}\n")
    print(f"\n>>> FULL ERROR TRACEBACK WRITTEN TO: {ERROR_LOG_PATH}\n")


def _log_security_event(event: str, user_id: Optional[uuid.UUID], detail: str) -> None:
    security_logger.warning("event=%s user_id=%s detail=%s", event, user_id, detail)


def extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
    case_id: uuid.UUID = Form(...),
    title: str = Form(...),
    document_type: str = Form(...),
    confidentiality_level: int = Form(default=1),
    evidence_item_id: Optional[uuid.UUID] = Form(None),
    document_number: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    # 1. Validate Document Type
    doc_type_clean = document_type.strip()
    if doc_type_clean not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid document_type. Must be one of: {', '.join(ALLOWED_DOC_TYPES)}"
        )
    
    # 2. Validate Confidentiality Level (e.g., 1 to 5)
    if not (1 <= confidentiality_level <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="confidentiality_level must be between 1 and 5."
        )
    
    # --- 3. RBAC ---
    await require_upload_permission(user, case_id)

    # --- 4. Pre-flight size check (defense in depth; not fully trustworthy alone) ---
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds maximum allowed size.")

    # --- 5. Streaming ingest to quarantine, chunked, hashing as we go ---
    quarantine_path = Path(settings.QUARANTINE_DIR) / f"{uuid.uuid4()}.part"
    hasher = sha256()
    bytes_written = 0

    try:
        async with aiofiles.open(quarantine_path, "wb") as out:
            while True:
                chunk = await file.read(settings.UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > settings.MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        "File exceeds maximum allowed size.",
                    )
                hasher.update(chunk)
                await out.write(chunk)

        file_hash = hasher.hexdigest()

        # --- 6. True MIME validation via magic bytes, not client-supplied header ---
        true_mime = detect_true_mime(str(quarantine_path))
        assert_allowed_mime(true_mime)

        # --- 7. Antivirus scan ---
        if settings.ENABLE_AV_SCAN:
            scan_result = await scan_file(str(quarantine_path))
            if scan_result.infected:
                _log_security_event("MALWARE_DETECTED", user.id, f"signature={scan_result.signature}")
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "File failed security scan.")
        else:
            _log_security_event("AV_SCAN_SKIPPED", user.id, "ENABLE_AV_SCAN=False - dev mode only")

        # --- 8. Upload to encrypted object storage ---
        document_uuid = uuid.uuid4()
        ext = extension_for_mime(true_mime)
        storage_key = f"case_{case_id}/{document_uuid}.{ext}"

        await upload_file(str(quarantine_path), storage_key, true_mime)

        # --- 9. Atomic DB write: document row + document_version row + audit entry together ---
        pool = get_pool()
        safe_filename = sanitize_display_filename(file.filename or "unnamed")

        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # Get user's department ID (needed for audit log)
                    user_dept = await conn.fetchval(
                        """
                        SELECT department_id 
                        FROM user_departments 
                        WHERE user_id = $1 AND is_primary = TRUE
                        """,
                        user.id
                    )
                    
                    if not user_dept:
                        raise HTTPException(
                            status.HTTP_400_BAD_REQUEST, 
                            "User has no department assigned. Cannot proceed."
                        )

                    # Insert into documents table (metadata)
                    await conn.execute(
                        """
                        INSERT INTO documents
                            (id, case_id, evidence_item_id, document_number, title,
                             document_type, confidentiality_level, current_version,
                             created_by, created_at, is_locked)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), false)
                        """,
                        document_uuid, case_id, evidence_item_id, document_number, title,
                        doc_type_clean, confidentiality_level, 1, user.id,
                    )

                    # Insert into document_versions table (file storage details)
                    version_id = await conn.fetchval(
                        """
                        INSERT INTO document_versions
                            (id, document_id, version_number, storage_uri, file_size_bytes,
                             file_mime_type, sha256_checksum, kms_key_id, uploaded_by, uploaded_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
                        RETURNING id
                        """,
                        uuid.uuid4(), document_uuid, 1, storage_key, bytes_written,
                        true_mime, file_hash, None, user.id,  # kms_key_id is None for now
                    )

                    # Write hash-chained audit entry with complete version tracking
                    entry_hash = await write_audit_entry(
                        conn=conn,
                        case_id=case_id,
                        document_id=document_uuid,
                        evidence_id=evidence_item_id,
                        actor_id=user.id,
                        actor_department_id=user_dept,
                        action="DOCUMENT_UPLOADED",
                        ip_address=extract_client_ip(request),
                        user_agent=request.headers.get("User-Agent"),
                        details={
                            "sha256": file_hash,
                            "size_bytes": bytes_written,
                            "mime": true_mime,
                            "version_id": str(version_id),
                            "version_number": 1,
                            "storage_key": storage_key,
                            "filename": safe_filename
                        }
                    )
        except Exception as db_exc:
            # DB write failed after object storage succeeded -> roll back storage too
            await delete_object(storage_key)
            _log_security_event("DB_ROLLBACK", user.id, f"storage_cleanup_performed: {str(db_exc)}")
            raise

        return DocumentUploadResponse(
            document_id=document_uuid,
            sha256=file_hash,
            status="active",
            audit_entry_hash=entry_hash,
        )

    except HTTPException:
        raise
    except Exception as exc:
        _log_full_traceback(f"UPLOAD_FAILURE user_id={user.id} case_id={case_id}")
        _log_security_event("UPLOAD_FAILURE", user.id, str(exc))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Upload could not be completed.")
    finally:
        # Always clean up the local quarantine file, success or failure.
        if quarantine_path.exists():
            quarantine_path.unlink(missing_ok=True)


# ============================================================
# 1. ENHANCED LIST: Fetch documents for a case with Pagination
# ============================================================
@router.get("/case/{case_id}", response_model=PaginatedDocumentsResponse, summary="List case documents")
async def list_case_documents(
    case_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """
    Data Flow: DB -> API -> Frontend
    Fetches documents for a specific case, joining with the latest version metadata.
    """
    offset = (page - 1) * limit
    
    # Build query dynamically based on filters
    query = """
        SELECT d.id, d.case_id, d.title, d.document_type, d.document_number,
               dv.file_size_bytes, dv.sha256_checksum, d.created_by, d.created_at,
               d.current_version, d.confidentiality_level, d.is_locked
        FROM documents d
        LEFT JOIN document_versions dv ON d.id = dv.document_id 
            AND dv.version_number = d.current_version
        WHERE d.case_id = $1
    """
    params = [case_id]
    param_idx = 2
    
    if doc_type:
        query += f" AND d.document_type = ${param_idx}"
        params.append(doc_type)
        param_idx += 1
        
    query += f" ORDER BY d.created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
    params.extend([limit, offset])
    
    async with db_pool.acquire() as conn:
        # Get total count
        count_query = "SELECT COUNT(*) FROM documents WHERE case_id = $1"
        total = await conn.fetchval(count_query, case_id)
        
        # Fetch records
        records = await conn.fetch(query, *params)
        
    return PaginatedDocumentsResponse(
        total=total,
        page=page,
        limit=limit,
        documents=[DocumentResponse(**dict(r)) for r in records]
    )


# ============================================================
# 2. GET SINGLE DOCUMENT
# ============================================================
@router.get("/{document_id}", response_model=DocumentResponse, summary="Get single document metadata")
async def get_document_by_id(
    document_id: uuid.UUID,
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """Fetch complete metadata for a single document."""
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow(
            """
            SELECT d.id, d.case_id, d.title, d.document_type, d.document_number,
                   dv.file_size_bytes, dv.sha256_checksum, d.created_by, d.created_at,
                   d.current_version, d.confidentiality_level, d.is_locked
            FROM documents d
            JOIN document_versions dv ON d.id = dv.document_id
                AND dv.version_number = d.current_version
            WHERE d.id = $1
            """,
            document_id
        )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse(**dict(record))


# ============================================================
# 3. AUDIT TRAIL: Fetch Immutable Chain of Custody
# ============================================================
@router.get("/{document_id}/audit", response_model=list[AuditLogResponse], summary="Get document audit trail")
async def get_document_audit_trail(
    document_id: uuid.UUID,
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """
    Data Flow: DB -> API -> Frontend
    CRITICAL FOR LEGAL VALIDITY: Returns the hash-chained history of the document.
    """
    async with db_pool.acquire() as conn:
        # First, verify user has access to this document's case
        doc = await conn.fetchrow("SELECT case_id FROM documents WHERE id = $1", document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        # TODO: Add RBAC check - await require_case_access(user, doc['case_id'])
        
        # Fetch audit logs ordered by time (newest first)
        logs = await conn.fetch(
            """
            SELECT id, case_id, document_id, evidence_id, actor_id, actor_department_id,
                   action, ip_address, user_agent, previous_log_hash, current_log_hash, created_at
            FROM chain_of_custody_logs
            WHERE document_id = $1
            ORDER BY created_at DESC
            """,
            document_id
        )
        
    return [AuditLogResponse(**dict(row)) for row in logs]


# ============================================================
# 4. UPDATE METADATA: Securely modify document properties
# ============================================================
@router.patch("/{document_id}", status_code=status.HTTP_200_OK, summary="Update document metadata")
async def update_document_metadata(
    document_id: uuid.UUID,
    updates: DocumentMetadataUpdate,
    request: Request,
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """
    Data Flow: Frontend -> API -> DB + Audit Log
    Updates metadata and IMMUTABLY logs the change in the chain of custody.
    """
    update_fields = []
    params = []
    param_idx = 1
    
    if updates.title is not None:
        update_fields.append(f"title = ${param_idx}")
        params.append(updates.title)
        param_idx += 1
        
    if updates.confidentiality_level is not None:
        if not (1 <= updates.confidentiality_level <= 5):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="confidentiality_level must be between 1 and 5."
            )
        update_fields.append(f"confidentiality_level = ${param_idx}")
        params.append(updates.confidentiality_level)
        param_idx += 1
        
    if updates.is_locked is not None:
        update_fields.append(f"is_locked = ${param_idx}")
        params.append(updates.is_locked)
        param_idx += 1
        
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")
        
    params.append(document_id)
    
    query = f"""
        UPDATE documents 
        SET {', '.join(update_fields)} 
        WHERE id = ${param_idx}
        RETURNING case_id
    """
    
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetchrow(query, *params)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
                
            case_id = result['case_id']
            
            # Get user's department
            user_dept = await conn.fetchval(
                "SELECT department_id FROM user_departments WHERE user_id = $1 AND is_primary = TRUE",
                user.id
            )
            
            # CRITICAL: Write to immutable audit log
            await write_audit_entry(
                conn=conn,
                case_id=case_id,
                document_id=document_id,
                evidence_id=None,
                actor_id=user.id,
                actor_department_id=user_dept,
                action="METADATA_UPDATED",
                ip_address=extract_client_ip(request),
                user_agent=request.headers.get("User-Agent"),
                details={"changes": updates.dict(exclude_none=True)}
            )
            
    return {"message": "Document metadata updated and audit log secured."}


# ============================================================
# 5. INTER-DEPARTMENT SHARE: Collaborative Data Movement
# ============================================================
@router.post("/{document_id}/share", status_code=status.HTTP_201_CREATED, summary="Share document with department")
async def share_document_with_department(
    document_id: uuid.UUID,
    share_req: ShareDocumentRequest,
    request: Request,
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """
    Data Flow: Frontend -> API -> DB (inter_department_shares)
    Grants another department access to this document.
    """
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # 1. Get document details
            doc = await conn.fetchrow(
                "SELECT case_id, created_by FROM documents WHERE id = $1", 
                document_id
            )
            if not doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
                
            # 2. Get user's department (source)
            source_dept = await conn.fetchval(
                "SELECT department_id FROM user_departments WHERE user_id = $1 AND is_primary = TRUE",
                user.id
            )
            
            if not source_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="User has no department assigned."
                )
            
            # 3. Insert share record
            share_id = uuid.uuid4()
            valid_from = datetime.now(timezone.utc)
            expires_at = valid_from + timedelta(days=share_req.expires_in_days)
            
            await conn.execute(
                """
                INSERT INTO inter_department_shares 
                (id, document_id, source_department_id, target_department_id, 
                 granted_by_user_id, access_level, reason, valid_from, expires_at, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'active')
                """,
                share_id, document_id, source_dept, share_req.target_department_id,
                user.id, share_req.access_level, share_req.reason, valid_from, expires_at
            )
            
            # 4. Audit the share action
            await write_audit_entry(
                conn=conn,
                case_id=doc['case_id'],
                document_id=document_id,
                evidence_id=None,
                actor_id=user.id,
                actor_department_id=source_dept,
                action="DOCUMENT_SHARED",
                ip_address=extract_client_ip(request),
                user_agent=request.headers.get("User-Agent"),
                details={
                    "target_department_id": str(share_req.target_department_id),
                    "access_level": share_req.access_level,
                    "expires_at": expires_at.isoformat(),
                    "reason": share_req.reason
                }
            )
            
    return {"message": "Document shared successfully", "share_id": str(share_id)}


# ============================================================
# 6. SECURE DOWNLOAD (Already implemented - kept for reference)
# ============================================================
@router.get("/{document_id}/download", response_model=DocumentDownloadResponse, summary="Get access URL & log audit")
async def get_secure_download_url(
    document_id: uuid.UUID,
    request: Request,
    db_pool: asyncpg.Pool = Depends(get_pool),
    user: AuthenticatedUser = Depends(verify_jwt),
):
    """Generate presigned download URL and log the access."""
    async with db_pool.acquire() as conn:
        # Get the latest version's storage key
        record = await conn.fetchrow(
            """
            SELECT d.id, d.case_id, d.document_number AS file_name, dv.storage_uri AS s3_key
            FROM documents d
            JOIN document_versions dv ON d.id = dv.document_id
                AND dv.version_number = d.current_version
            WHERE d.id = $1
            """,
            document_id
        )
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Get user's department
        user_dept = await conn.fetchval(
            "SELECT department_id FROM user_departments WHERE user_id = $1 AND is_primary = TRUE",
            user.id
        )

        await log_audit_event(
            conn=conn,
            case_id=record['case_id'],
            document_id=document_id,
            actor_id=user.id,
            actor_department_id=user_dept,
            action="PRESIGNED_URL_GENERATED",
            ip_address=extract_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            extra_details={"download_initiated": True}
        )

    presigned_url = await generate_presigned_download_url(
        record["s3_key"],
        file_name=record["file_name"]
    )

    return DocumentDownloadResponse(
        document_id=record["id"],
        file_name=record["file_name"],
        presigned_url=presigned_url,
        expires_in_seconds=300
    )
