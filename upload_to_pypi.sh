#!/bin/bash
# PyPI upload script

# Check if a PyPI token is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <pypi_token>"
  echo "Please provide your PyPI API token as an argument"
  exit 1
fi

# Set up environment variables for twine
export TWINE_USERNAME=__token__
export TWINE_PASSWORD="$1"

# Go to project directory
cd "$(dirname "$0")" || exit 1

# Build the package (if needed)
echo "Building the package..."
poetry build

# Check package files with twine
echo "Checking package files..."
twine check dist/*

# Show files to be uploaded
echo "The following files will be uploaded to PyPI:"
find dist -name "projectprompt-1.0.1*" -type f -print

# Confirmation
read -p "Do you want to upload these files to PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Upload aborted by user"
  exit 0
fi

# Upload to PyPI
echo "Uploading to PyPI..."
find dist -name "projectprompt-1.0.1*" -type f -exec twine upload {} \;

echo "Upload process completed!"
