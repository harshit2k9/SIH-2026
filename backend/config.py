from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- PostgreSQL Components ---
    # Support both individual vars and full DATABASE_URL for cloud deployments (Render, etc.)
    DATABASE_URL: str | None = None  # Full connection string (e.g., from Render)
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def DATABASE_URL_COMPUTED(self) -> str:
        # If DATABASE_URL is provided directly (e.g., from Render), use it
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Otherwise build from individual components
        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB, self.POSTGRES_SERVER]):
            raise ValueError("Either DATABASE_URL or all POSTGRES_* variables must be set")
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sih26.db"

    # Connection pool tuning
    DB_POOL_MIN_SIZE: int = 10
    DB_POOL_MAX_SIZE: int = 30
    DB_COMMAND_TIMEOUT: float = 10.0
    DB_MAX_INACTIVE_LIFETIME: float = 300.0
    DB_STATEMENT_CACHE_SIZE: int = 1024

    # --- JWT ---
    JWT_PUBLIC_KEY_PATH: str = "keys/public.pem"
    JWT_PRIVATE_KEY_PATH: str = "keys/private.pem"  # ✅ ADDED: Required for /api/auth/token
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = "sddms-api"
    JWT_ISSUER: str = "sddms-auth-service"

    # --- MinIO / S3-compatible storage ---
    MINIO_ENDPOINT_URL: str = "http://minio:9000"
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    
    MINIO_BUCKET: str = "legal-documents"
    
    # ⚠️ CRITICAL: Must be False for local Docker (http://minio:9000). 
    # Only set to True in production behind an HTTPS reverse proxy.
    MINIO_USE_SSL: bool = False  
    MINIO_ENABLE_SSE: bool = True  # ✅ Enforce Server-Side Encryption

    # --- ClamAV ---
    CLAMAV_HOST: str = "clamav"  # Defaults to Docker service name
    CLAMAV_PORT: int = 3310
    CLAMAV_TIMEOUT: float = 15.0
    ENABLE_AV_SCAN: bool = True

    # --- Upload constraints ---
    # Note: If MAX_FILE_SIZE_BYTES is in .env (e.g., 2048576000), it will override this default.
    MAX_FILE_SIZE_BYTES: int = 200 * 1024 * 1024  
    UPLOAD_CHUNK_SIZE: int = 1 * 1024 * 1024
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