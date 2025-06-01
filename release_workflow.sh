#!/bin/bash

# ProjectPrompt Release Workflow Script
# This script handles commit, push, merge, and PyPI release

set -e  # Exit on any error

echo "🚀 Starting ProjectPrompt Release Workflow"
echo "=========================================="

# Step 1: Add all changes and commit
echo "📝 Step 1: Adding and committing changes..."
git add .

git commit -m "feat: Complete testing framework and enhanced rules system

- Add comprehensive testing suite with 16 test files  
- Implement enhanced rules management system
- Add rule models with YAML export functionality
- Create structured rules integration  
- Add testing documentation and reports
- Implement AI-powered rules analysis
- Add rules wizard and templates
- Complete test coverage for all commands
- Add execution summary and reporting tools
- Ready for PyPI release v1.2.7"

echo "✅ Changes committed successfully"

# Step 2: Push current branch
echo "📤 Step 2: Pushing feature branch..."
git push origin feature/rules-categories

echo "✅ Feature branch pushed successfully"

# Step 3: Switch to main and merge
echo "🔄 Step 3: Switching to main branch..."
git checkout main

echo "📥 Step 4: Pulling latest main..."
git pull origin main

echo "🔗 Step 5: Merging feature branch..."
git merge feature/rules-categories

echo "✅ Feature branch merged successfully"

# Step 4: Update version in pyproject.toml
echo "📈 Step 6: Updating version to 1.2.7..."
sed -i 's/version = "1.2.6"/version = "1.2.7"/' pyproject.toml

# Commit version bump
git add pyproject.toml
git commit -m "bump: version 1.2.7 - Complete testing framework and enhanced rules"

echo "✅ Version updated to 1.2.7"

# Step 5: Push main
echo "📤 Step 7: Pushing updated main branch..."
git push origin main

echo "✅ Main branch pushed successfully"

# Step 6: Create git tag
echo "🏷️ Step 8: Creating release tag..."
git tag -a v1.2.7 -m "Release v1.2.7: Complete testing framework and enhanced rules system"
git push origin v1.2.7

echo "✅ Release tag created and pushed"

# Step 7: Build for PyPI
echo "📦 Step 9: Building package for PyPI..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Install build dependencies if needed
pip install --upgrade build twine

# Build the package
python -m build

echo "✅ Package built successfully"

# Step 8: Upload to PyPI (you'll need to confirm this step)
echo "🚀 Step 10: Ready to upload to PyPI"
echo ""
echo "Your package is ready! To upload to PyPI, run:"
echo "  python -m twine upload dist/*"
echo ""
echo "Or for test PyPI first:"
echo "  python -m twine upload --repository testpypi dist/*"
echo ""

# Show build artifacts
echo "📋 Build artifacts created:"
ls -la dist/

echo ""
echo "🎉 Release workflow completed successfully!"
echo "=========================================="
echo "Summary:"
echo "- ✅ Changes committed and pushed"
echo "- ✅ Feature branch merged to main"  
echo "- ✅ Version bumped to 1.2.7"
echo "- ✅ Release tag v1.2.7 created"
echo "- ✅ Package built for PyPI"
echo "- 🔄 Ready for PyPI upload (manual step)"
echo ""
echo "Next: Upload to PyPI with the twine command above"
