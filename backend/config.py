"""
Centralized settings. Never hardcode secrets — all pulled from environment
variables / .env file. Fail loudly at startup if critical secrets are missing.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- PostgreSQL ---
    DATABASE_URL: str  # e.g. postgresql://user:pass@host:5432/dbname

    # Connection pool tuning (see README for reasoning)
    DB_POOL_MIN_SIZE: int = 10
    DB_POOL_MAX_SIZE: int = 30
    DB_COMMAND_TIMEOUT: float = 10.0
    DB_MAX_INACTIVE_LIFETIME: float = 300.0
    DB_STATEMENT_CACHE_SIZE: int = 1024   # set to 0 if PgBouncer is in transaction-pooling mode

    # --- JWT (RS256 — asymmetric, so the API only ever needs the PUBLIC key) ---
    JWT_PUBLIC_KEY_PATH: str = "keys/public.pem"
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = "sddms-api"
    JWT_ISSUER: str = "sddms-auth-service"

    # --- MinIO / S3-compatible storage ---
    MINIO_ENDPOINT_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "legal-documents"
    MINIO_USE_SSL: bool = False
    MINIO_ENABLE_SSE: bool = False   # Set False for local MinIO without a KMS provider configured.
                                     # Production (real S3/MinIO+KMS): keep True.

    # --- ClamAV ---
    CLAMAV_HOST: str = "localhost"
    CLAMAV_PORT: int = 3310
    CLAMAV_TIMEOUT: float = 15.0
    ENABLE_AV_SCAN: bool = True   # DEV ONLY: set False in .env to skip ClamAV while it's not set up.
                                  # NEVER set this False in production — malware scanning is mandatory
                                  # for a legal/evidence document system.

    # --- Upload constraints ---
    MAX_FILE_SIZE_BYTES: int = 200 * 1024 * 1024   # 200 MB, tune per case-file expectations
    UPLOAD_CHUNK_SIZE: int = 1 * 1024 * 1024        # 1 MB streaming chunks
    QUARANTINE_DIR: str = "/tmp/sddms_quarantine"
    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "video/mp4",
        "audio/mpeg",
    }

    # --- Rate limiting ---
    RATE_LIMIT_UPLOAD: str = "20/minute"


settings = Settings()
