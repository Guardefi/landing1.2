# Multi-stage Dockerfile for Core Orchestrator

# === STAGE 1: Base ===
# Pinned digest for python:3.11-slim (security hardening)
FROM python@sha256:7e61c0ad2f7ba28cd4b78df90f9e6ec83b3fa5ad5265b0e7b5a8e5e6e6c9b3e2 as base

LABEL maintainer="Scorpius Enterprise Platform"
LABEL description="Core Orchestrator for service management and plugin coordination"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# === STAGE 2: Development ===
FROM base as development

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install with dev dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir watchdog pytest pytest-asyncio black ruff

# Copy source code
COPY . .

# Create user
RUN groupadd -r scorpius && useradd -r -g scorpius scorpius
RUN chown -R scorpius:scorpius /app

USER scorpius

# Expose ports
EXPOSE 8001 8002

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "orchestrator_new:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# === STAGE 3: Production ===
FROM base as production

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core orchestrator code
COPY core/orchestrator_new.py .
COPY core/config.py .
COPY core/types.py .
COPY core/__init__.py .

# Create non-root user
RUN groupadd -r scorpius && useradd -r -g scorpius scorpius
RUN chown -R scorpius:scorpius /app
USER scorpius

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import asyncio; import redis.asyncio as redis; asyncio.run(redis.from_url('redis://redis:6379').ping())"

# Expose port
EXPOSE 8001

# Run the orchestrator
CMD ["python", "-m", "uvicorn", "orchestrator_new:app", "--host", "0.0.0.0", "--port", "8001"]
