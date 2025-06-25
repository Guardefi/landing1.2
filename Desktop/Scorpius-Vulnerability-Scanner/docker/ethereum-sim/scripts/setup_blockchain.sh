#!/bin/bash
# Setup blockchain environment for simulation

set -e

echo "Setting up Ethereum simulation environment..."

# Start Ganache in background
ganache \
    --host 0.0.0.0 \
    --port 8545 \
    --accounts 10 \
    --defaultBalanceEther 1000 \
    --gasLimit 8000000 \
    --gasPrice 20000000000 \
    --mnemonic "scorpius test mnemonic for simulation purposes only" \
    --networkId 1337 \
    --quiet &

GANACHE_PID=$!

# Wait for Ganache to start
echo "Waiting for Ganache to start..."
sleep 5

# Verify connection
curl -X POST \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
    http://localhost:8545

echo "Ganache started successfully with PID: $GANACHE_PID"
echo "Blockchain is ready for simulation"

# Save PID for cleanup
echo $GANACHE_PID > /tmp/ganache.pid
