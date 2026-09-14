import asyncio
import logging
from typing import Optional
import aioboto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, EndpointConnectionError
from config import settings

logger = logging.getLogger(__name__) # FIXED: __name__

_boto_config = BotoConfig(max_pool_connections=50, retries={"max_attempts": 3, "mode": "standard"}, connect_timeout=5, read_timeout=30)
_session = aioboto3.Session()

def _client_kwargs():
    return dict(
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        use_ssl=settings.MINIO_USE_SSL,
        config=_boto_config,
    )

async def ensure_bucket(max_retries: int = 5, delay: float = 2.0) -> None:
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
                logger.error(f"Could not connect to S3 endpoint after {max_retries} attempts.")
                raise e
            await asyncio.sleep(delay)

async def upload_file(local_path: str, storage_key: str, content_type: str) -> None:
    extra_args = {"ContentType": content_type}
    
    # FIXED: Typo MINIO_E NABLE_SSE -> MINIO_ENABLE_SSE
    if getattr(settings, "MINIO_ENABLE_SSE", False):
        extra_args["ServerSideEncryption"] = "AES256"
        if not settings.MINIO_USE_SSL:
            logger.warning(f"SSE enabled but SSL disabled for {storage_key}")

    async with _session.client("s3", **_client_kwargs()) as s3:
        with open(local_path, "rb") as f:
            await s3.upload_fileobj(f, settings.MINIO_BUCKET, storage_key, ExtraArgs=extra_args)

async def delete_object(storage_key: str) -> None:
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=storage_key)

async def generate_presigned_download_url(storage_key: str, file_name: Optional[str] = None, expires_in: int = 300) -> str:
    params = {"Bucket": settings.MINIO_BUCKET, "Key": storage_key}
    if file_name:
        params["ResponseContentDisposition"] = f'attachment; filename="{file_name}"'
        
    async with _session.client("s3", **_client_kwargs()) as s3:
        url = await s3.generate_presigned_url("get_object", Params=params, ExpiresIn=expires_in)
    return url