FROM --platform=linux/amd64 python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies for pypdf / Textract client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code only (exclude tests, venv, .env)
COPY app/ app/

EXPOSE 8000

# 2 workers for Fargate 256 CPU / 512 MB
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
