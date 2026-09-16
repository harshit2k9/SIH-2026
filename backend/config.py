from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, Field
from typing import Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- PostgreSQL Components ---
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "postgres"  # Defaults to Docker service name
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str

    @computed_field
    @property
    def DATABASE_URL_COMPUTED(self) -> str:
        # If DATABASE_URL is provided (e.g., by Render), use it directly
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Otherwise, build from individual components
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            # Use POSTGRES_HOST if available (for Render), otherwise use POSTGRES_SERVER
            host = self.POSTGRES_HOST or self.POSTGRES_SERVER
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # Fallback to SQLite for local development
        return "sqlite:///./sih26.db"

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
    ENABLE_AV_SCAN: bool = False  # Disabled to allow all file uploads without virus scan

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
