# Ethereum Simulation Environment for Exploit Testing
FROM node:18-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Hardhat and related tools
RUN npm install -g hardhat
RUN npm install -g @nomiclabs/hardhat-ethers
RUN npm install -g ethers
RUN npm install -g @openzeppelin/contracts

# Install Ganache for local blockchain
RUN npm install -g ganache

# Install Foundry (Forge, Cast, Anvil)
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"
RUN /root/.foundry/bin/foundryup

# Install Solidity compiler
RUN curl -L https://github.com/ethereum/solidity/releases/download/v0.8.19/solc-static-linux \
    -o /usr/local/bin/solc && chmod +x /usr/local/bin/solc

# Create workspace directories
RUN mkdir -p /workspace/contracts /workspace/exploits /workspace/reports

# Copy simulation scripts
COPY scripts/ /workspace/scripts/
RUN chmod +x /workspace/scripts/*.sh

# Create non-root user for security
RUN useradd -m -u 1000 simulator && \
    chown -R simulator:simulator /workspace

# Install Python packages for exploit development
RUN pip3 install web3 eth-account eth-utils

USER simulator
WORKDIR /workspace

# Set environment variables
ENV NODE_ENV=development
ENV HARDHAT_NETWORK=localhost
ENV ETH_RPC_URL=http://localhost:8545

# Expose ports for local blockchain
EXPOSE 8545 8546

# Default command (keeps container running)
CMD ["tail", "-f", "/dev/null"]
