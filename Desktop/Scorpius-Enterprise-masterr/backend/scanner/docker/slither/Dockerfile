# Enhanced Slither Docker Image for Scorpius
FROM python:3.9-slim

LABEL maintainer="Scorpius Security Team"
LABEL description="Containerized Slither static analysis for smart contracts"
LABEL scorpius.plugin="slither"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler (multiple versions)
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux \
    -o /usr/local/bin/solc-0.8.19 && chmod +x /usr/local/bin/solc-0.8.19
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.7.6/solc-static-linux \
    -o /usr/local/bin/solc-0.7.6 && chmod +x /usr/local/bin/solc-0.7.6
RUN ln -s /usr/local/bin/solc-0.8.19 /usr/local/bin/solc

# Install Slither and dependencies
RUN pip install --no-cache-dir \
    slither-analyzer \
    crytic-compile \
    solc-select \
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
RUN useradd -m -u 1000 slither && \
    chown -R slither:slither /workspace

USER slither
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace

ENTRYPOINT ["/entrypoint.sh"]
ENV SOLC_VERSION=0.8.19

# Expose API port
EXPOSE 8081

# Default command starts the API server
CMD ["python", "/workspace/app.py"]
