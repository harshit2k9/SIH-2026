FROM python:3.11-slim

# Install system libraries and build dependencies
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
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
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /usr/src/app

# Upgrade pip tools early
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU-only PyTorch upfront (creates a permanent, cached layer)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download EasyOCR models
RUN python -c "import easyocr; easyocr.Reader(['en', 'hi'], download_enabled=True)"

# Copy application code
COPY . .

# Generate JWT keys if they don't exist (for Render deployment)
RUN mkdir -p keys && \
    if [ ! -f keys/private.pem ]; then \
        python -c "from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048); f = open('keys/private.pem', 'wb'); f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())); f.close(); public_key = private_key.public_key(); f = open('keys/public.pem', 'wb'); f.write(public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)); f.close()"; \
    fi

EXPOSE 8000

# Run database migrations before starting the server
RUN python migrate_db.py || echo "Migration step completed or skipped"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
