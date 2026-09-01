"""
Never trust client-supplied filenames or Content-Type headers.
- Storage paths use a server-generated UUID, never the client filename.
- The client filename is kept ONLY as sanitized display metadata.
- Actual file type is determined by reading magic bytes (python-magic),
  not by trusting the extension or the multipart Content-Type field —
  both are trivially spoofable.
"""
import re

import magic

from config import settings

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\- ]")


def sanitize_display_filename(filename: str) -> str:
    """Strip path components and dangerous characters; used for display/metadata only."""
    name = filename.replace("\\", "/").split("/")[-1]   # strip any path traversal attempt
    name = _SAFE_FILENAME_RE.sub("_", name)
    return name[:255]


def detect_true_mime(file_path: str) -> str:
    """Reads the first bytes of the file on disk to determine its real type."""
    mime = magic.from_file(file_path, mime=True)
    return mime


def assert_allowed_mime(mime: str) -> None:
    if mime not in settings.ALLOWED_MIME_TYPES:
        from fastapi import HTTPException, status
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"File type '{mime}' is not permitted.",
        )


def extension_for_mime(mime: str) -> str:
    return {
        "application/pdf": "pdf",
        "image/png": "png",
        "image/jpeg": "jpg",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "video/mp4": "mp4",
        "audio/mpeg": "mp3",
    }.get(mime, "bin")
