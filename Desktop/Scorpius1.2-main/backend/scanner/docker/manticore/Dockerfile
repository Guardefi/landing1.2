# Enhanced Manticore Docker Image for Scorpius
FROM python:3.9-slim

LABEL maintainer="Scorpius Security Team"
LABEL description="Containerized Manticore symbolic execution for smart contracts"
LABEL scorpius.plugin="manticore"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    software-properties-common \
    libssl-dev \
    libffi-dev \
    cmake \
    z3 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux \
    -o /usr/local/bin/solc && chmod +x /usr/local/bin/solc

# Install Manticore and dependencies
RUN pip install --no-cache-dir \
    manticore[native] \
    z3-solver \
    pysha3 \
    crytic-compile \
    fastapi \
    uvicorn \
    python-multipart

# Create workspace directories
WORKDIR /workspace
RUN mkdir -p /workspace/input /workspace/output

# Create Manticore runner script
COPY manticore_runner.py /app/manticore_runner.py
COPY app.py /workspace/app.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN groupadd -r manticore && useradd -r -g manticore manticore
RUN chown -R manticore:manticore /workspace /app
USER manticore

ENTRYPOINT ["/entrypoint.sh"]
ENV MANTICORE_TIMEOUT=600

# Expose API port
EXPOSE 8083

# Default command starts the API server
CMD ["python", "/workspace/app.py"]
