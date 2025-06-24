# Advanced Vulnerability Scanner Service Dockerfile
# Contains Slither, Mythril, Manticore, Echidna, and other professional security analysis tools

FROM python:3.11-slim

# Install system dependencies including development headers for crypto compilation
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libc6-dev \
    libgmp-dev \
    libsecp256k1-dev \
    nodejs \
    npm \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for some tools)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Go (required for some tools)
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Install multiple Solidity compiler versions
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux > /usr/local/bin/solc-0.8.19 \
    && chmod +x /usr/local/bin/solc-0.8.19 \
    && curl -L https://github.com/ethereum/solidity/releases/download/v0.8.20/solc-static-linux > /usr/local/bin/solc-0.8.20 \
    && chmod +x /usr/local/bin/solc-0.8.20 \
    && curl -L https://github.com/ethereum/solidity/releases/download/v0.8.21/solc-static-linux > /usr/local/bin/solc-0.8.21 \
    && chmod +x /usr/local/bin/solc-0.8.21 \
    && ln -s /usr/local/bin/solc-0.8.19 /usr/local/bin/solc

# Set working directory
WORKDIR /app

# Upgrade pip and install wheel
RUN pip install --upgrade pip setuptools wheel

# Install crypto dependencies first (to handle pysha3 compilation)
RUN pip install --no-cache-dir \
    setuptools-rust \
    cffi \
    pycparser \
    cryptography \
    pycryptodome \
    coincurve

# Install core Python security tools and dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    aiohttp==3.9.1 \
    pydantic==2.5.0 \
    web3==6.11.3 \
    eth-abi==4.2.1 \
    requests==2.31.0 \
    eth-utils \
    eth-typing \
    eth-hash[pycryptodome]

# Install advanced security analysis tools
RUN pip install --no-cache-dir \
    slither-analyzer==0.10.0 \
    mythril==0.24.8 \
    crytic-compile \
    manticore[native] \
    pyevmasm

# Install additional useful tools
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-asyncio==0.21.1 \
    py-solc-x \
    solc-select

# Copy scanner service code
COPY scanner/ /app/

# Create results directory
RUN mkdir -p /app/results

# Create directories for tool outputs
RUN mkdir -p /app/outputs/slither /app/outputs/mythril /app/outputs/manticore /app/outputs/echidna

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the scanner service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
