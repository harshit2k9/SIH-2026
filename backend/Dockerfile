FROM python:3.11-slim

# Install system libraries and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "2"]