# Multi-stage Dockerfile for API Gateway
# API Gateway - Production Docker Image
FROM python:3.11-slim
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/api-gateway/requirements.txt .
COPY packages/core/ /build/core/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Install core package from mounted volume
RUN pip install --no-cache-dir --no-build-isolation \
    --use-pep517 \
    --no-cache-dir \
    --no-deps \
    /build/core

# Copy configuration files first
COPY services/api-gateway/alembic.ini ./

# Copy migrations directory
COPY services/api-gateway/migrations/ ./migrations/

# Copy application code
COPY services/api-gateway/. .

# Ensure files have correct permissions
RUN chmod 644 alembic.ini && chmod 755 entrypoint.sh

# Create non-root user
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=$PATH:/app

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE ${PORT}

# Copy entrypoint and set as executable
COPY --chmod=755 services/api-gateway/entrypoint.sh .

# Set entrypoint and user
ENTRYPOINT ["./entrypoint.sh"]
USER appuser

# Command is set in entrypoint.sh
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:${PORT}"]
