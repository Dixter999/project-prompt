#!/bin/bash

# ProjectPrompt Workspace Cleanup Script
# This script removes test files and keeps only essential user files for v1.2.7

echo "🧹 ProjectPrompt Workspace Cleanup - Keeping Only Essential Files"
echo "================================================================="

# Essential files to keep (core functionality)
ESSENTIAL_FILES=(
    "pyproject.toml"
    "README.md" 
    "CHANGELOG.md"
    "LICENSE"
    "MANIFEST.in"
    "requirements.txt"
    "poetry.lock"
    "CODE_OF_CONDUCT.md"
    "CONTRIBUTING.md"
    "SECURITY.md"
    "ROADMAP.md"
    "config.yaml.example"
    ".gitignore"
)

# Essential directories to keep
ESSENTIAL_DIRS=(
    "src/"
    "docs/"
    "examples/"
    "tests/"
)

# Files and directories to remove (test files, temporary files, etc.)
FILES_TO_REMOVE=(
    # Test files created during development
    "test_*.py"
    "test_*.sh"
    "*test*.py"
    "basic_test.py"
    "simple_test.py"
    "demo_*.py"
    "final_*.py"
    "direct_*.py"
    "validate_*.py"
    
    # Test results and temporary directories
    "test-results-*/"
    "project-output/"
    "__pycache__/"
    "*.pyc"
    "*.pyo"
    
    # Development and completion reports
    "*_COMPLETION*.md"
    "*_SUCCESS*.md"
    "*_STATUS*.py"
    "*_REPORT*.md"
    "PHASE_*.md"
    "FINAL_*.md"
    "ULTIMATE_*.md"
    "ENHANCED_*.md"
    "STRUCTURED_*.md"
    "TESTING_*.md"
    "IMPLEMENTATION_*.py"
    "QUICKSTART_*.md"
    
    # Temporary and demo files
    "analyze_help.txt"
    "help_output.txt"
    "version_output.txt"
    "*.log"
    "*.tmp"
    
    # Release and development scripts
    "release_workflow.sh"
    "pypi_upload_instructions.sh"
    "implement_project_prompt_rules"
    
    # Project-specific rule files created during testing
    "project-prompt-*.md"
    "test_rules.yaml"
    "rule_models_test_report.md"
    "test-ai-suggestions.md"
)

# Count files before cleanup
echo "📊 Files before cleanup:"
find . -type f | wc -l

echo ""
echo "🗑️ Removing unnecessary files..."

# Remove test and temporary files
for pattern in "${FILES_TO_REMOVE[@]}"; do
    echo "Removing: $pattern"
    find . -name "$pattern" -type f -exec rm -f {} \; 2>/dev/null
    find . -name "$pattern" -type d -exec rm -rf {} \; 2>/dev/null
done

# Remove empty directories
echo ""
echo "🧹 Removing empty directories..."
find . -type d -empty -delete 2>/dev/null

echo ""
echo "📊 Files after cleanup:"
find . -type f | wc -l

echo ""
echo "✅ Essential files preserved:"
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ⚠ $file (not found)"
    fi
done

echo ""
echo "✅ Essential directories preserved:"
for dir in "${ESSENTIAL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ⚠ $dir (not found)"
    fi
done

echo ""
echo "🎯 Workspace cleaned! Only essential user files remain for v1.2.7."
echo "📦 Ready for clean PyPI release."
