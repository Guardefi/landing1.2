#!/bin/bash
# Fund an address with ETH

set -e

ADDRESS=$1
AMOUNT=$2

if [ -z "$ADDRESS" ] || [ -z "$AMOUNT" ]; then
    echo "Usage: $0 <address> <amount_in_wei>"
    exit 1
fi

echo "Funding address $ADDRESS with $AMOUNT wei..."

# Use cast to send ETH
cast send \
    --rpc-url http://localhost:8545 \
    --private-key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d \
    --value $AMOUNT \
    $ADDRESS

echo "Successfully funded address $ADDRESS"
