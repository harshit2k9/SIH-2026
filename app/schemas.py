from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: int
    sha256: str
    status: str
    audit_entry_hash: str


class ErrorResponse(BaseModel):
    detail: str
