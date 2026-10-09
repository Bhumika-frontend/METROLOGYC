FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies for Tesseract OCR and Barcode (zbar)
# Note: GUI libs (libgl1, libglib2.0-0) are omitted because opencv-python-headless is used
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code, preloaded database, and uploads
COPY backend /app/backend
COPY data /app/data
COPY uploads /app/uploads

# Create non-root appuser and grant full permissions to writable directories (/app, /app/data, /app/uploads)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app/backend

# Expose port (Render/Koyeb inject PORT environment variable)
EXPOSE 8080

# Start FastAPI with Uvicorn — single worker + concurrency cap to prevent OOM on 512MB instances
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --limit-concurrency 2 --log-level info"]
