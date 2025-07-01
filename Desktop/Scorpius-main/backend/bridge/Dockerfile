# Multi-stage Dockerfile for enterprise production deployment
ARG PYTHON_VERSION=3.11

# Base stage with common dependencies
FROM python:${PYTHON_VERSION}-slim as base

# Set build arguments
ARG BUILD_ENV=production
ARG APP_USER=scorpius
ARG APP_UID=1000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g ${APP_UID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_USER} -m -s /bin/bash ${APP_USER}

# Set work directory
WORKDIR /app

# Dependencies stage
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements-prod.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-warn-script-location -r requirements-prod.txt

# Development stage
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from dependencies stage
COPY --from=dependencies /usr/local /usr/local

# Copy development requirements and install
COPY requirements.txt ./
RUN pip install --no-warn-script-location -r requirements.txt

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs && chown -R ${APP_USER}:${APP_USER} logs

# Switch to non-root user
USER ${APP_USER}

# Expose ports
EXPOSE 8000 50051

# Development command
CMD ["uvicorn", "scorpius_bridge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Test stage
FROM development as test

# Switch back to root for test dependencies
USER root

# Install test dependencies
RUN pip install pytest pytest-cov pytest-asyncio httpx

# Switch back to app user
USER ${APP_USER}

# Run tests
CMD ["pytest", "tests/", "-v", "--cov=scorpius_bridge", "--cov-report=term-missing"]

# Production stage
FROM base as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local /usr/local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} . .

# Create logs directory with proper ownership
RUN mkdir -p logs && chown -R ${APP_USER}:${APP_USER} logs

# Remove unnecessary files
RUN rm -rf \
    tests/ \
    docs/ \
    *.md \
    .git* \
    .env* \
    docker-compose* \
    deploy.sh \
    requirements.txt

# Switch to non-root user
USER ${APP_USER}

# Expose ports
EXPOSE 8000 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with multiple workers
CMD ["uvicorn", "scorpius_bridge.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]
