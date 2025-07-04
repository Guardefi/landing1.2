#!/bin/bash
# Slither entrypoint script

set -e

# Default to analyzing all contracts in input directory
INPUT_DIR="/workspace/input"
OUTPUT_DIR="/workspace/output"

# Find Solidity files
CONTRACT_FILE="${INPUT_DIR}/contract.sol"

if [ ! -f "$CONTRACT_FILE" ]; then
    echo "Error: No contract.sol found in ${INPUT_DIR}" >&2
    exit 1
fi

# Run Slither analysis
echo "Running Slither analysis on ${CONTRACT_FILE}..."

# Create output file
OUTPUT_FILE="${OUTPUT_DIR}/results.json"

# Run Slither with JSON output
slither "$CONTRACT_FILE" \
    --json "$OUTPUT_FILE" \
    --disable-color \
    --exclude-dependencies \
    --exclude-informational \
    --exclude-low \
    --exclude-optimization \
    || {
        # If Slither fails, create empty results file
        echo '{"results": {"detectors": []}, "error": "Analysis failed"}' > "$OUTPUT_FILE"
    }

echo "Slither analysis completed. Results saved to ${OUTPUT_FILE}"
