# Main Scorpius Application Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    software-properties-common \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/contracts /workspace/reports /workspace/config /workspace/logs

# Create non-root user for security
RUN useradd -m -u 1000 scorpius && \
    chown -R scorpius:scorpius /app /workspace

# Install additional security tools
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard] \
    fastapi \
    sqlalchemy \
    psycopg2-binary \
    redis \
    celery \
    prometheus_client

USER scorpius

# Set environment variables
ENV PYTHONPATH=/app
ENV SCORPIUS_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
