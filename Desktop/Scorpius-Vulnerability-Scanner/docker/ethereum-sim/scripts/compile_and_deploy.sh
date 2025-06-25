#!/bin/bash
# Compile and deploy contract

set -e

CONTRACT_FILE=$1

if [ -z "$CONTRACT_FILE" ]; then
    echo "Usage: $0 <contract_file>"
    exit 1
fi

echo "Compiling and deploying contract: $CONTRACT_FILE"

# Compile with solc
CONTRACT_NAME=$(basename "$CONTRACT_FILE" .sol)
solc --bin --abi --optimize --overwrite -o /tmp/compiled/ "$CONTRACT_FILE"

if [ ! -f "/tmp/compiled/${CONTRACT_NAME}.bin" ]; then
    echo "Compilation failed - no bytecode generated"
    exit 1
fi

# Deploy using cast
BYTECODE=$(cat "/tmp/compiled/${CONTRACT_NAME}.bin")
DEPLOYMENT_TX=$(cast send \
    --rpc-url http://localhost:8545 \
    --private-key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d \
    --create \
    "0x$BYTECODE" \
    --json)

CONTRACT_ADDRESS=$(echo "$DEPLOYMENT_TX" | jq -r '.contractAddress')

echo "Contract deployed at address: $CONTRACT_ADDRESS"
echo "Deployment transaction: $(echo "$DEPLOYMENT_TX" | jq -r '.transactionHash')"
echo "$CONTRACT_ADDRESS" > /tmp/contract_address.txt

# Save ABI for later use
if [ -f "/tmp/compiled/${CONTRACT_NAME}.abi" ]; then
    cp "/tmp/compiled/${CONTRACT_NAME}.abi" "/workspace/reports/contract.abi"
fi
