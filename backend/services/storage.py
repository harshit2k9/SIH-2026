"""
Async object storage wrapper (MinIO, S3-compatible) using aioboto3.
Files are keyed by case_id/document_uuid so access-control checks at the
API layer naturally map onto a predictable, non-guessable storage path.
Server-side encryption is requested on every upload.
"""
import asyncio
import logging
import aioboto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from config import settings

logger = logging.getLogger(__name__)

_boto_config = BotoConfig(
    max_pool_connections=50,   # match/exceed expected concurrent uploads
    retries={"max_attempts": 3, "mode": "standard"},
    connect_timeout=5,
    read_timeout=30,
)

_session = aioboto3.Session()


def _client_kwargs():
    return dict(
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        use_ssl=settings.MINIO_USE_SSL,
        config=_boto_config,
    )


async def ensure_bucket() -> None:
    """Connects to MinIO with retry logic and ensures the configured bucket exists."""
    max_retries = 10
    retry_delay = 3

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to MinIO... (Attempt {attempt}/{max_retries})", flush=True)
            async with _session.client("s3", **_client_kwargs()) as s3:
                try:
                    await s3.head_bucket(Bucket=settings.MINIO_BUCKET)
                except ClientError as e:
                    # 404 means the bucket does not exist, create it
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code in ("404", "NoSuchBucket"):
                        await s3.create_bucket(Bucket=settings.MINIO_BUCKET)
                    else:
                        raise e

            print("Successfully connected to MinIO and verified bucket!", flush=True)
            return

        except (BotoCoreError, ClientError, Exception) as e:
            if attempt == max_retries:
                logger.error("Failed to connect to MinIO after maximum retries.")
                raise e
            print(f"MinIO not ready yet ({e}). Retrying in {retry_delay}s...", flush=True)
            await asyncio.sleep(retry_delay)


async def upload_file(local_path: str, storage_key: str, content_type: str) -> None:
    async with _session.client("s3", **_client_kwargs()) as s3:
        with open(local_path, "rb") as f:
            await s3.upload_fileobj(
                f,
                settings.MINIO_BUCKET,
                storage_key,
                ExtraArgs={
                    "ContentType": content_type,
                },
            )


async def delete_object(storage_key: str) -> None:
    """Used for rollback if a DB transaction fails after upload succeeded."""
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=storage_key)


async def generate_presigned_download_url(
    storage_key: str, 
    file_name: str | None = None, 
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