#!/bin/bash
# TestPyPI upload script - For testing purposes only

# Check if a TestPyPI token is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <testpypi_token>"
  echo "Please provide your TestPyPI API token as an argument"
  exit 1
fi

# Set up environment variables for twine
export TWINE_USERNAME=__token__
export TWINE_PASSWORD="$1"

# Go to project directory
cd "$(dirname "$0")" || exit 1

# Build the package
echo "Building the package..."
poetry build

# Check package files with twine
echo "Checking package files..."
twine check dist/*

# Show files to be uploaded
echo "The following files will be uploaded to TestPyPI:"
find dist -name "projectprompt-1.0.2*" -type f -print

# Confirmation
read -p "Do you want to upload these files to TestPyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Upload aborted by user"
  exit 0
fi

# Upload to TestPyPI
echo "Uploading to TestPyPI..."
find dist -name "projectprompt-1.0.2*" -type f -exec twine upload --repository-url https://test.pypi.org/legacy/ {} \;

echo "Upload process completed!"
echo "You can test the installation using:"
echo "pip install --index-url https://test.pypi.org/simple/ projectprompt"
