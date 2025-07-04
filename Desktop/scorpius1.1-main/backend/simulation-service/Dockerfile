FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install minimal Python dependencies for FastAPI server
RUN pip install \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.5.0 \
    pydantic-settings>=2.0.0 \
    httpx>=0.25.0 \
    requests>=2.31.0

# Copy application
COPY . .

# Create workspace
RUN mkdir -p workspace

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8006

# Use the simple API server instead of the complex module structure
CMD ["python", "simple_simulation_api.py"]
