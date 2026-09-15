FROM python:3.11-slim

# Install system libraries and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxcb1 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Upgrade pip tools early
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
# Install CPU-only PyTorch upfront (creates a permanent, cached layer)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import easyocr; easyocr.Reader(['en', 'hi'], download_enabled=True)"

# Copy application code (excluding files in .dockerignore)
COPY . .

# Run database migrations before starting the server
# Provide default env vars for build-time migration (will be overridden at runtime)
ENV MINIO_ROOT_USER=minio_admin
ENV MINIO_ROOT_PASSWORD=minio_secure_password_2025
ENV POSTGRES_USER=sddms_user
ENV POSTGRES_PASSWORD=sddms_secure_password_2025
ENV POSTGRES_DB=sddms_db
ENV POSTGRES_SERVER=postgres
ENV POSTGRES_PORT=5432

RUN python migrate_db.py || echo "Migration completed or skipped"

# Ensure schema tables exist (idempotent) - using schema file copied with the app
RUN python -c "\
import psycopg2; \
from config import settings; \
conn = psycopg2.connect(settings.DATABASE_URL_COMPUTED); \
cur = conn.cursor(); \
cur.execute(open('SIH_DATABASE.sql').read()); \
conn.commit(); \
cur.close(); \
conn.close(); \
print('✅ Schema verified')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "2"]