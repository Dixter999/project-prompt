#!/bin/bash
# Script to test the VS Code extension publishing command locally

# This script simulates the GitHub Actions publishing step

# Set this to your actual PAT for testing (or leave empty to skip actual publishing)
VSCE_PAT="" 

echo "=== Starting VS Code extension publishing test ==="

# Install vsce globally if needed
if ! command -v vsce &> /dev/null; then
  echo "Installing @vscode/vsce..."
  npm install -g @vscode/vsce
fi

# Create a temporary directory for publishing
mkdir -p temp_publish

# Copy the VSIX files (if they exist)
echo "Looking for VSIX files in vscode-extension directory..."
if find vscode-extension -name "*.vsix" -exec cp {} temp_publish/ \; ; then
  echo "Files copied to temp_publish/"
else
  echo "No VSIX files found in vscode-extension directory"
  # Try to build one
  echo "Attempting to build VSIX file..."
  cd vscode-extension
  vsce package --no-dependencies
  cd ..
  find vscode-extension -name "*.vsix" -exec cp {} temp_publish/ \;
fi

# List the files in the temp directory
echo "Files in temp_publish directory:"
ls -la temp_publish/

# Simulate or perform publishing
for file in temp_publish/*.vsix; do
  if [ -f "$file" ]; then
    echo "Would publish: $file"
    
    # Uncomment to actually publish if VSCE_PAT is set
    if [ -n "$VSCE_PAT" ]; then
      echo "Publishing $file"
      vsce publish --packagePath "$file" -p "$VSCE_PAT"
    else
      echo "(Skipping actual publishing - no PAT provided)"
    fi
  fi
done

echo "=== Test complete ==="
