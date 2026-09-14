from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class DocumentUploadResponse(BaseModel):
    document_id: UUID
    sha256: str
    status: str
    audit_entry_hash: str

class ErrorResponse(BaseModel):
    detail: str

class DocumentResponse(BaseModel):
    id: UUID
    case_id: UUID
    title: str
    document_type: str
    document_number: Optional[str] = None
    current_version: int
    confidentiality_level: int
    file_size_bytes: Optional[int] = None  # Optional in case version join fails
    sha256_checksum: Optional[str] = None
    created_by: UUID
    created_at: datetime
    is_locked: bool
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedDocumentsResponse(BaseModel):
    total: int
    page: int
    limit: int
    documents: List[DocumentResponse]

class DocumentDownloadResponse(BaseModel):
    document_id: UUID
    file_name: str
    presigned_url: str
    expires_in_seconds: int

class AuditLogResponse(BaseModel):
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
    current_log_hash: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentMetadataUpdate(BaseModel):
    title: Optional[str] = None
    confidentiality_level: Optional[int] = Field(None, ge=1, le=5)
    is_locked: Optional[bool] = None

class ShareDocumentRequest(BaseModel):
    target_department_id: UUID
    access_level: str = Field(..., pattern="^(read|write|admin)$")
    reason: str = Field(..., min_length=5)
    expires_in_days: int = Field(default=30, ge=1, le=365)

class DocumentVersionResponse(BaseModel):
    document_id: UUID
    new_version_number: int
    sha256: str
    audit_entry_hash: str