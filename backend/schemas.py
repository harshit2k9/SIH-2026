from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# DOCUMENT SCHEMAS
# ============================================================

class DocumentUploadResponse(BaseModel):
    document_id: UUID
    version_number: int
    sha256: str
    status: str
    audit_entry_hash: str


class ErrorResponse(BaseModel):
    detail: str


class DocumentResponse(BaseModel):
    id: UUID
    case_id: UUID
    evidence_item_id: Optional[UUID] = None
    document_number: str
    title: str
    document_type: str
    confidentiality_level: Optional[int] = Field(default=1, ge=1, le=5)
    current_version: Optional[int] = 1
    created_by: Optional[UUID] = None
    created_at: datetime
    is_locked: bool = False

    # Optional fields populated when joined with document_versions
    file_size_bytes: Optional[int] = None
    sha256_checksum: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocumentsResponse(BaseModel):
    total: int
    page: int
    limit: int
    documents: List[DocumentResponse]


class DocumentDownloadResponse(BaseModel):
    document_id: UUID
    file_name: str  # Maps to document_number or title
    presigned_url: str
    expires_in_seconds: int


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    storage_uri: str
    file_size_bytes: Optional[int] = None
    file_mime_type: Optional[str] = None
    sha256_checksum: Optional[str] = None
    kms_key_id: Optional[str] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentMetadataUpdate(BaseModel):
    title: Optional[str] = None
    confidentiality_level: Optional[int] = Field(None, ge=1, le=5)
    is_locked: Optional[bool] = None


# ============================================================
# CHAIN OF CUSTODY / AUDIT SCHEMAS
# ============================================================

class ChainOfCustodyLogResponse(BaseModel):
    id: UUID
    case_id: UUID
    document_id: Optional[UUID] = None
    evidence_id: Optional[UUID] = None
    actor_id: UUID
    actor_department_id: UUID
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    previous_log_hash: Optional[str] = None
    current_log_hash: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Backwards compatibility alias for AuditLogResponse
AuditLogResponse = ChainOfCustodyLogResponse


# ============================================================
# INTER-DEPARTMENT SHARING SCHEMAS
# ============================================================

class ShareDocumentRequest(BaseModel):
    target_department_id: UUID
    access_level: str = Field(..., pattern="^(read|write|admin)$")
    reason: str
    valid_from: Optional[datetime] = None
    expires_in_days: int = Field(default=30, ge=1, le=365)


class InterDepartmentShareResponse(BaseModel):
    id: UUID
    document_id: UUID
    source_department_id: UUID
    target_department_id: UUID
    granted_by_user_id: UUID
    access_level: str
    reason: Optional[str] = None
    valid_from: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)