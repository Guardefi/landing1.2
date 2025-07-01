# Multi-stage production Dockerfile with security hardening
# Pinned digest for python:3.11-slim (security hardening)
FROM python@sha256:7e61c0ad2f7ba28cd4b78df90f9e6ec83b3fa5ad5265b0e7b5a8e5e6e6c9b3e2 AS base

LABEL maintainer="Scorpius Enterprise Platform"
LABEL description="MEV Bot - Production"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mevuser && chown -R mevuser:mevuser /app
USER mevuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "mev_guardian_bot.py"]
