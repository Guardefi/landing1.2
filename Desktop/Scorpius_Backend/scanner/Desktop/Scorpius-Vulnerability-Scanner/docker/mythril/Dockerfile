# Enhanced Mythril Docker Image for Scorpius
FROM python:3.9-slim

LABEL maintainer="Scorpius Security Team"
LABEL description="Containerized Mythril symbolic execution for smart contracts"
LABEL scorpius.plugin="mythril"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    software-properties-common \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux \
    -o /usr/local/bin/solc && chmod +x /usr/local/bin/solc

# Install Mythril and dependencies
RUN pip install --no-cache-dir \
    mythril \
    py-solc-x \
    solc-select \
    web3 \
    fastapi \
    uvicorn \
    python-multipart

# Create workspace directories
WORKDIR /workspace
RUN mkdir -p /workspace/input /workspace/output

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
COPY app.py /workspace/app.py
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN groupadd -r mythril && useradd -r -g mythril mythril
RUN chown -R mythril:mythril /workspace
USER mythril

# Initialize Mythril
RUN myth version

ENTRYPOINT ["/entrypoint.sh"]

# Expose API port
EXPOSE 8082

# Default command starts the API server
CMD ["python", "/workspace/app.py"]
