from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: int
    sha256: str
    status: str
    audit_entry_hash: str


class ErrorResponse(BaseModel):
    detail: str


class DocumentResponse(BaseModel):
    id: int
    case_id: int
    title: str
    document_type: str
    original_filename: str
    file_size_bytes: int
    sha256_hash: str
    uploaded_by: int
    created_at: datetime


class PaginatedDocumentsResponse(BaseModel):
    total: int
    page: int
    limit: int
    documents: List[DocumentResponse]


class DocumentDownloadResponse(BaseModel):
    document_id: int
    file_name: str
    presigned_url: str
    expires_in_seconds: int