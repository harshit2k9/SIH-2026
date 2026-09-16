"""
Async file storage using local filesystem.
Files are stored by case_id/document_uuid so access-control checks at the
API layer naturally map onto a predictable, non-guessable storage path.
"""
import asyncio
import logging
import os
import shutil
from typing import Optional
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)

# Ensure storage directory exists
STORAGE_DIR = Path("/tmp/sddms_storage")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Retry configuration
MAX_RETRIES = 5
RETRY_DELAY = 2.0  # seconds


async def ensure_bucket(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY) -> None:
    """Ensure the storage directory exists (no-op for local filesystem)."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Storage directory ready: {STORAGE_DIR}")
    return


async def upload_file(local_path: str, storage_key: str, content_type: str) -> None:
    """Upload a file to local filesystem storage."""
    # Create full path for storage
    full_storage_path = STORAGE_DIR / storage_key
    
    # Ensure parent directories exist
    full_storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file to storage location
    shutil.copy2(local_path, full_storage_path)
    
    logger.debug(f"Uploaded file to storage key: {storage_key}")


async def delete_object(storage_key: str) -> None:
    """Used for rollback if a DB transaction fails after upload succeeded."""
    full_storage_path = STORAGE_DIR / storage_key
    if full_storage_path.exists():
        full_storage_path.unlink()
    logger.debug(f"Deleted object from storage key: {storage_key}")
    



async def generate_presigned_download_url(
    storage_key: str,
    file_name: Optional[str] = None,
    expires_in: int = 300
) -> str:
    """Generate a download URL for local filesystem storage."""
    # For local filesystem, return a direct path or API endpoint
    # In production, you might want to serve this through an API route
    full_path = STORAGE_DIR / storage_key
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {storage_key}")
    
    # Return API endpoint for downloading (since we can't expose local paths directly)
    # The actual download will be handled by an API route
    return f"/api/documents/download/{storage_key}"


async def get_object_metadata(storage_key: str) -> dict:
    """Retrieve metadata about an object without downloading it."""
    full_path = STORAGE_DIR / storage_key
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {storage_key}")
    
    stat = full_path.stat()
    return {
        "content_length": stat.st_size,
        "content_type": "application/octet-stream",  # Default, could be enhanced with mime detection
        "last_modified": stat.st_mtime,
        "etag": None,  # Not applicable for local filesystem
    }