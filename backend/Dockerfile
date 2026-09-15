FROM python:3.11-slim

# Install Node.js 20.x for building frontend
RUN rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    (apt-get update --fix-missing || apt-get update) && \
    apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install system libraries and build dependencies
RUN (apt-get update --fix-missing || apt-get update) && \
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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /usr/src/app

# Upgrade pip tools early
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU-only PyTorch upfront (creates a permanent, cached layer)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy and install frontend dependencies
COPY ../frontend/package*.json ./frontend/
WORKDIR /usr/src/app/frontend
RUN npm install

# Install backend dependencies
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download EasyOCR models
RUN python -c "import easyocr; easyocr.Reader(['en', 'hi'], download_enabled=True)"

# Copy application code (excluding files in .dockerignore)
COPY . .

# Build frontend for production
WORKDIR /usr/src/app/frontend
RUN npm run build

# Copy built frontend to backend static directory
WORKDIR /usr/src/app
RUN mkdir -p static && cp -r frontend/dist/* static/ || echo "Frontend build copied or skipped"

EXPOSE 8000

# Run database migrations before starting the server
# On Render, migrations run at runtime when DB is available
RUN python migrate_db.py || echo "Migration step completed or skipped (will run at container start)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "2"]
