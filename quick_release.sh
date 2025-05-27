#!/bin/bash
# ProjectPrompt v1.0.0 Quick Release Script
# Simplified version to avoid terminal issues

set -e

echo "🚀 ProjectPrompt v1.0.0 Quick Release"
echo "======================================"

cd /mnt/h/Projects/project-prompt

echo "📍 Current directory: $(pwd)"
echo "📋 Current commit: $(git rev-parse --short HEAD)"

# Check if we're on the right commit (bae57fc)
current_commit=$(git rev-parse --short HEAD)
if [[ "$current_commit" != "bae57fc"* ]]; then
    echo "⚠️  Warning: Expected commit bae57fc*, got $current_commit"
fi

# Switch to main branch
echo "🌿 Creating main branch..."
git checkout -B main

# Push to GitHub
echo "🚀 Pushing to GitHub..."
if git push origin main --force-with-lease; then
    echo "✅ Successfully pushed to GitHub"
else
    echo "⚠️  Force push failed, trying regular push..."
    git push origin main
fi

# Create and push tag
echo "🏷️  Creating release tag v1.0.0..."
git tag -d v1.0.0 2>/dev/null || true  # Delete if exists
git tag -a v1.0.0 -m "Release 1.0.0: Stable release with core functionality"
git push origin v1.0.0

# Test installation
echo "🧪 Testing package installation..."
pip install -e . --quiet

# Test CLI
echo "🔧 Testing CLI functionality..."
python3 -m src.main --version

echo ""
echo "✅ RELEASE DEPLOYMENT COMPLETE!"
echo "================================"
echo "🔗 GitHub: https://github.com/Dixter999/project-prompt"
echo "🏷️  Tag: v1.0.0 created and pushed"
echo "📦 Package ready for PyPI upload"
echo ""
echo "Next steps:"
echo "1. Check GitHub Actions: https://github.com/Dixter999/project-prompt/actions"
echo "2. Upload to PyPI: python3 -m twine upload dist/*"
echo "3. Test install: pip install projectprompt"
