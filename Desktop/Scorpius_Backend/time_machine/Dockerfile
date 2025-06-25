# Multi-stage Dockerfile for Time Machine Application

# Stage 1: Build React UI
FROM node:18-alpine AS ui-builder

WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm ci --only=production

COPY ui/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Copy built UI from first stage
COPY --from=ui-builder --chown=app:app /app/ui/build ./ui/build

# Create necessary directories
RUN mkdir -p store/snapshots store/bundles logs config && \
    chown -R app:app /app

# Switch to app user
USER app

# Configuration is already copied with the app code

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "time_machine_app.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
