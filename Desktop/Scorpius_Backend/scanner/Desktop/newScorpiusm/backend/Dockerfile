FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools and Python dev headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    python3-setuptools \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libc6-dev \
    pkg-config \
    software-properties-common \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Solidity compiler
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler
RUN npm install -g solc@0.8.19

# Install Rust for Echidna and other Rust-based tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Go for additional security tools
RUN wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz \
    && rm go1.21.0.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Install pycryptodome as modern alternative to pysha3
RUN pip install --no-cache-dir pycryptodome

# Install security analysis tools one by one to handle errors gracefully
# Install Mythril (Ethereum smart contract security analyzer)
RUN pip install --no-cache-dir mythril

# Install Slither (Solidity static analyzer) 
RUN pip install --no-cache-dir slither-analyzer

# Install crytic-compile (latest stable version)
RUN pip install --no-cache-dir crytic-compile

# Try to install Manticore, fallback if it fails
RUN pip install --no-cache-dir manticore || \
    echo "Manticore installation failed due to pysha3 compilation issues, using alternative approach" && \
    pip install --no-cache-dir --no-binary=all --force-reinstall pysha3==1.0.2 || \
    echo "Using system without Manticore - other tools will still work"

# Install additional security tools
RUN pip install pyevmasm

# Install Foundry (includes anvil, cast, forge, chisel)
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"
RUN foundryup

# Set environment variables for tools
ENV MYTHRIL_DIR="/root/.mythril"
ENV SLITHER_HOME="/app"

# Copy the backend code
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

# Expose the API and WebSocket ports
EXPOSE 8000
EXPOSE 8081

# Start both servers using the startup script
CMD ["./start.sh"]
