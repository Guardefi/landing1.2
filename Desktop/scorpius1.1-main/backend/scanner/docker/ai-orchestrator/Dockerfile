# Enhanced AI Orchestrator Scanner for Scorpius
FROM python:3.11-slim

LABEL maintainer="Scorpius Security Team"
LABEL description="AI-powered vulnerability scanner orchestrator"
LABEL scorpius.plugin="ai-orchestrator"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    software-properties-common \
    libssl-dev \
    libffi-dev \
    python3-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler (multiple versions)
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux \
    -o /usr/local/bin/solc-0.8.19 && chmod +x /usr/local/bin/solc-0.8.19
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.7.6/solc-static-linux \
    -o /usr/local/bin/solc-0.7.6 && chmod +x /usr/local/bin/solc-0.7.6
RUN ln -s /usr/local/bin/solc-0.8.19 /usr/local/bin/solc

# Install Node.js dependencies for Hardhat
RUN npm install -g hardhat @nomiclabs/hardhat-ethers ethers

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    aiohttp \
    anthropic \
    openai \
    numpy \
    pandas \
    scikit-learn \
    web3 \
    eth-utils \
    python-jose \
    passlib \
    pydantic \
    asyncio-mqtt \
    redis \
    sqlalchemy \
    psycopg2-binary

# Create workspace directories
WORKDIR /workspace
RUN mkdir -p /workspace/input /workspace/output /workspace/temp

# Copy AI orchestrator files
COPY app.py /workspace/app.py
COPY orchestrator.py /workspace/orchestrator.py
COPY ai_analyzer.py /workspace/ai_analyzer.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 aiorch && \
    chown -R aiorch:aiorch /workspace

USER aiorch
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace
ENV SOLC_VERSION=0.8.19

ENTRYPOINT ["/entrypoint.sh"]

# Expose API port
EXPOSE 8000

# Default command starts the AI orchestrator API server
CMD ["python", "/workspace/app.py"] 