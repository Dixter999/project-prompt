#!/bin/bash
# ProjectPrompt v1.0.0 PyPI Release Script

set -e

echo "🚀 ProjectPrompt v1.0.0 - Final PyPI Release"
echo "============================================"

cd /mnt/h/Projects/project-prompt

# Verify we have the distribution files
echo "📦 Checking distribution files..."
if [ -f "dist/projectprompt-1.0.0-py3-none-any.whl" ] && [ -f "dist/projectprompt-1.0.0.tar.gz" ]; then
    echo "✅ Distribution files found:"
    ls -la dist/projectprompt-1.0.0*
else
    echo "❌ Distribution files missing, rebuilding..."
    poetry build
fi

# Test package installation locally
echo ""
echo "🧪 Testing local installation..."
pip install --force-reinstall dist/projectprompt-1.0.0-py3-none-any.whl

# Test CLI functionality
echo ""
echo "🔧 Testing CLI functionality..."
project-prompt --version || echo "⚠️ Version command issue"
project-prompt --help | head -5 || echo "⚠️ Help command issue"

echo ""
echo "📤 Ready for PyPI upload!"
echo "Run this command to upload to PyPI:"
echo "  python3 -m twine upload dist/projectprompt-1.0.0*"
echo ""
echo "Or for TestPyPI first:"
echo "  python3 -m twine upload --repository testpypi dist/projectprompt-1.0.0*"
echo ""
echo "After upload, test with:"
echo "  pip install projectprompt"
echo "  project-prompt --help"
