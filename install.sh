#!/bin/bash
# ProjectPrompt Enhanced Installation Script
# This script ensures proper CLI setup and PATH configuration

set -e

echo "🚀 ProjectPrompt Enhanced Installation"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null || echo "Not found")
echo "📦 Python version: $python_version"

# Install the package
echo "📥 Installing ProjectPrompt..."
pip install -e . || {
    echo "❌ Installation failed. Trying with user flag..."
    pip install --user -e .
}

# Verify installation
echo "🔍 Verifying installation..."
if python -c "import src.cli" 2>/dev/null; then
    echo "✅ ProjectPrompt module installed successfully"
else
    echo "⚠️  Module import issue - check your Python path"
fi

# Test CLI access
echo "🧪 Testing CLI access..."
if command -v projectprompt >/dev/null 2>&1; then
    echo "✅ projectprompt command available in PATH"
    projectprompt --help | head -3
elif python -m src.cli --help >/dev/null 2>&1; then
    echo "✅ CLI accessible via: python -m src.cli"
    python -m src.cli --help | head -3
else
    echo "⚠️  CLI not directly accessible - see manual setup below"
fi

# Manual setup instructions
echo ""
echo "🔧 Manual Setup (if needed):"
echo "Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
echo "   alias projectprompt='python -m src.cli'"
echo ""
echo "📋 Next Steps:"
echo "1️⃣  Restart terminal or run: source ~/.bashrc"
echo "2️⃣  Test: projectprompt --help"
echo "3️⃣  See README.md for usage examples"
echo ""
echo "🎉 Installation complete!"
