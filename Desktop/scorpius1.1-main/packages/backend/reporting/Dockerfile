# Scorpius Reporting Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/reports/pdf /app/reports/sarif /app/reports/signed \
    /app/templates /app/fonts /app/certs /app/audit_logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash scorpius && \
    chown -R scorpius:scorpius /app
USER scorpius

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Expose port
EXPOSE 8007

# Start command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8007", "--workers", "1"]
