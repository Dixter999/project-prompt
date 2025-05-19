#!/bin/bash
# Script to run Anthropic verification with the new directory structure

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set Python path to include the project root
export PYTHONPATH="$BASE_DIR/.."

# Check for API key
if [ -z "$anthropic_API" ]; then
    if [ -f "$BASE_DIR/../.env" ]; then
        source "$BASE_DIR/../.env"
    fi
fi

if [ -z "$anthropic_API" ]; then
    echo "Error: Anthropic API key not found."
    echo "Please set the anthropic_API environment variable or create a .env file."
    exit 1
fi

# Run verification
echo "Running Anthropic verification..."
python "$BASE_DIR/anthropic/enhanced_verify_anthropic.py" "$@"
