from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

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
    # current_version comes from documents table
    current_version: int
    confidentiality_level: int
    # file details come from document_versions table (joined)
    file_size_bytes: int
    sha256_checksum: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedDocumentsResponse(BaseModel):
    total: int
    page: int
    limit: int
    documents: List[DocumentResponse]


class DocumentDownloadResponse(BaseModel):
    document_id: UUID
    file_name: str  # This maps to document_number in your query
    presigned_url: str
    expires_in_seconds: int