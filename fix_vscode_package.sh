#!/bin/bash
# Script to remove both .vscodeignore and "files" property to fix packaging

set -e  # Exit on error

echo "=== Starting VSCode extension fix ==="
cd /mnt/h/Projects/project-prompt/vscode-extension

echo "=== Removing .vscodeignore file if it exists ==="
if [ -f .vscodeignore ]; then
  echo "Found .vscodeignore file, removing it"
  rm .vscodeignore
  echo "File removed"
else
  echo "No .vscodeignore file found"
fi

echo "=== Checking if 'files' property exists in package.json ==="
if grep -q '"files"' package.json; then
  echo "Found 'files' property in package.json"
  # We'll handle this manually since jq might not be installed
  echo "Please remove the 'files' property manually from package.json"
else
  echo "No 'files' property found in package.json"
fi

echo "=== Creating a simple .vscodeignore file ==="
cat > .vscodeignore << 'EOL'
.vscode/**
.github/**
node_modules/**
test/**
src/**
!src/index.js
!src/panel.js
!src/providers/**
!src/integrations/**
**/*.map
*.ts
EOL
echo ".vscodeignore file created with minimal content"

echo "=== Building extension package ==="
echo "Running: npx @vscode/vsce package --no-dependencies"
npx @vscode/vsce package --no-dependencies

echo "=== Fix script complete ==="
echo "If the packaging was successful, you should see a .vsix file in this directory"
ls -la *.vsix
