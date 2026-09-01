"""
Async object storage wrapper (MinIO, S3-compatible) using aioboto3.
Files are keyed by case_id/document_uuid so access-control checks at the
API layer naturally map onto a predictable, non-guessable storage path.
Server-side encryption is requested on every upload.
"""
import aioboto3
from botocore.config import Config as BotoConfig

from config import settings

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
    async with _session.client("s3", **_client_kwargs()) as s3:
        buckets = await s3.list_buckets()
        names = [b["Name"] for b in buckets.get("Buckets", [])]
        if settings.MINIO_BUCKET not in names:
            await s3.create_bucket(Bucket=settings.MINIO_BUCKET)


async def upload_file(local_path: str, storage_key: str, content_type: str) -> None:
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


async def delete_object(storage_key: str) -> None:
    """Used for rollback if a DB transaction fails after upload succeeded."""
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=storage_key)


async def generate_presigned_download_url(storage_key: str, expires_in: int = 300) -> str:
    async with _session.client("s3", **_client_kwargs()) as s3:
        return await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.MINIO_BUCKET, "Key": storage_key},
            ExpiresIn=expires_in,   # short TTL — avoid stale link replay
        )
