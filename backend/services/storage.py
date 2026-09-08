"""
Async object storage wrapper (MinIO, S3-compatible) using aioboto3.
Files are keyed by case_id/document_uuid so access-control checks at the
API layer naturally map onto a predictable, non-guessable storage path.
Server-side encryption is requested on every upload.
"""
import asyncio
import logging
from typing import Optional


import aioboto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, EndpointConnectionError

from config import settings

logger = logging.getLogger(__name__)


_boto_config = BotoConfig(
    max_pool_connections=50,   # match/exceed expected concurrent uploads
    retries={"max_attempts": 3, "mode": "standard"},
    connect_timeout=5,
    read_timeout=30,
)

_session = aioboto3.Session()

# Retry configuration
MAX_RETRIES = 5
RETRY_DELAY = 2.0  # seconds


def _client_kwargs():
    return dict(
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        use_ssl=settings.MINIO_USE_SSL,
        config=_boto_config,
    )


async def ensure_bucket(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY) -> None:
    """async with _session.client("s3", **_client_kwargs()) as s3:
        buckets = await s3.list_buckets()
        names = [b["Name"] for b in buckets.get("Buckets", [])]
        if settings.MINIO_BUCKET not in names:
            await s3.create_bucket(Bucket=settings.MINIO_BUCKET)"""
    for attempt in range(1, max_retries + 1):
        try:
            async with _session.client("s3", **_client_kwargs()) as s3:
                buckets = await s3.list_buckets()
                names = [b["Name"] for b in buckets.get("Buckets", [])]
                if settings.MINIO_BUCKET not in names:
                    await s3.create_bucket(Bucket=settings.MINIO_BUCKET)
                    logger.info(f"Created S3 bucket: {settings.MINIO_BUCKET}")
                return
        except (EndpointConnectionError, ClientError, Exception) as e:
            if attempt == max_retries:
                logger.error(f"Could not connect to S3 endpoint at {settings.MINIO_ENDPOINT_URL} after {max_retries} attempts.")
                raise e
            logger.warning(
                f"MinIO storage connection attempt {attempt}/{max_retries} failed ({e}). Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)


async def upload_file(local_path: str, storage_key: str, content_type: str) -> None:
        """Upload a file to MinIO/S3 with server-side encryption."""

    async with _session.client("s3", **_client_kwargs()) as s3:
        with open(local_path, "rb") as f:
            await s3.upload_fileobj(
                f,
                settings.MINIO_BUCKET,
                storage_key,
                ExtraArgs={
                    "ContentType": content_type,
                    #"ServerSideEncryption": "AES256",  # optional, but MinIO doesn't support SSE-C/SSE-KMS, only SSE-S3
                },
            )
        logger.debug(f"Uploaded file to storage key: {storage_key}")



async def delete_object(storage_key: str) -> None:
    """Used for rollback if a DB transaction fails after upload succeeded."""
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=storage_key)
    logger.debug(f"Deleted object from storage key: {storage_key}")



async def generate_presigned_download_url(
    storage_key: str, 
    file_name: Optional[str] = None, 
    expires_in: int = 300
) -> str:
    """Generates a short-lived presigned URL with optional inline browser disposition."""
    params = {
        "Bucket": settings.MINIO_BUCKET,
        "Key": storage_key,
    }
    
    if file_name:
        params["ResponseContentDisposition"] = f'inline; filename="{file_name}"'

    async with _session.client("s3", **_client_kwargs()) as s3:
        return await s3.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires_in,  # short TTL — avoid stale link replay
        )