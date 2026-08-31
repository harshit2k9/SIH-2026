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
  9. Single DB transaction: insert document row + hash-chained audit entry
  10. Return minimal metadata (never expose internal storage path)

Every failure path cleans up the quarantine file and (if applicable) the
uploaded MinIO object, and logs a security event without leaking internal
details to the client.
"""
import logging
import traceback
import uuid
from hashlib import sha256
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.database import get_pool
from app.schemas import DocumentUploadResponse
from app.security.auth import AuthenticatedUser, verify_jwt
from app.security.rbac import require_upload_permission
from app.security.sanitize import assert_allowed_mime, detect_true_mime, extension_for_mime, sanitize_display_filename
from app.services import storage
from app.services.antivirus import scan_file
from app.services.audit import write_audit_entry

router = APIRouter(prefix="/documents", tags=["documents"])
security_logger = logging.getLogger("security_events")
limiter = Limiter(key_func=get_remote_address)

Path(settings.QUARANTINE_DIR).mkdir(parents=True, exist_ok=True)

# Dedicated error log file — guarantees the full traceback lands somewhere
# findable, regardless of terminal scrollback or logging config quirks.
ERROR_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "upload_errors.log"


def _log_full_traceback(context: str) -> None:
    tb_text = traceback.format_exc()
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*80}\n{context}\n{'='*80}\n{tb_text}\n")
    print(f"\n>>> FULL ERROR TRACEBACK WRITTEN TO: {ERROR_LOG_PATH}\n")


def _log_security_event(event: str, user_id: int | None, detail: str) -> None:
    security_logger.warning("event=%s user_id=%s detail=%s", event, user_id, detail)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
    case_id: int = Form(...),
    title: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(verify_jwt),
):
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

        await storage.upload_file(str(quarantine_path), storage_key, true_mime)

        # --- 9. Atomic DB write: document row + audit entry together ---
        pool = get_pool()
        safe_filename = sanitize_display_filename(file.filename or "unnamed")

        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    document_id = await conn.fetchval(
                        """
                        INSERT INTO documents
                            (case_id, title, document_type, original_filename,
                             uploaded_by, status, storage_key, mime_type,
                             file_size_bytes, sha256_hash, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, 'active', $6, $7, $8, $9, NOW(), NOW())
                        RETURNING id
                        """,
                        case_id, title, document_type, safe_filename,
                        user.id, storage_key, true_mime, bytes_written, file_hash,
                    )
                    entry_hash = await write_audit_entry(
                        conn,
                        document_id=document_id,
                        actor_id=user.id,
                        action="UPLOAD",
                        details={"sha256": file_hash, "size_bytes": bytes_written, "mime": true_mime},
                    )
        except Exception:
            # DB write failed after object storage succeeded -> roll back storage too
            await storage.delete_object(storage_key)
            raise

        return DocumentUploadResponse(
            document_id=document_id,
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
