#!/usr/bin/env bash
# Script for final verification and deployment of ProjectPrompt
# This version is the complete verification script prior to publication

set -e  # Stop on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Command line arguments
SKIP_TESTS=false
SKIP_FREEMIUM=false
SKIP_ANTHROPIC=false
SKIP_VSCODE=false

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --skip-tests)
            SKIP_TESTS=true
            ;;
        --skip-freemium)
            SKIP_FREEMIUM=true
            ;;
        --skip-anthropic)
            SKIP_ANTHROPIC=true
            ;;
        --skip-vscode)
            SKIP_VSCODE=true
            ;;
        --help)
            echo "Usage: ./verify_and_deploy.sh [options]"
            echo "Options:"
            echo "  --skip-tests     Skip running unit and integration tests"
            echo "  --skip-freemium  Skip freemium system verification"
            echo "  --skip-anthropic Skip Anthropic integration verification"
            echo "  --skip-vscode    Skip building VS Code extension"
            echo "  --help           Show this help message"
            exit 0
            ;;
    esac
done

# Print banner
echo -e "${BLUE}"
echo "=================================================================="
echo "     ProjectPrompt - Final Verification and Release Preparation"
echo "=================================================================="
echo -e "${NC}"

# Base project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ------------------------------------------------------------
# SECTION 1: Environment and dependency verification
# ------------------------------------------------------------
echo -e "\n${YELLOW}[1/7] Verifying environment and dependencies...${NC}"

# Check Python
python_version=$(python3 --version 2>&1)
if [[ $python_version =~ Python\ 3\.([0-9]+)\.[0-9]+ ]]; then
    version="${BASH_REMATCH[1]}"
    if (( version >= 11 )); then
        echo -e "✓ ${GREEN}Python detected: $python_version${NC}"
    else
        echo -e "✗ ${YELLOW}Python version is lower than recommended. Python 3.11 or higher is recommended.${NC}"
        read -p "Continue anyway? [y/N] " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "✗ ${RED}Python 3.x not found. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

# Check dependencies
echo -e "Verifying Python dependencies..."
missing_deps=0

check_dependency() {
    local pkg=$1
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "✓ ${GREEN}$pkg installed${NC}"
        return 0
    else
        echo -e "✗ ${RED}$pkg not found${NC}"
        return 1
    fi
}

# List of critical dependencies
deps=("json" "pathlib" "requests" "setuptools" "argparse")
for dep in "${deps[@]}"; do
    check_dependency "$dep" || ((missing_deps++))
done

if [ $missing_deps -gt 0 ]; then
    echo -e "\n${RED}[ERROR] Missing $missing_deps dependencies. Install them with:${NC}"
    echo -e "pip install -r requirements.txt"
    exit 1
else
    echo -e "${GREEN}All basic dependencies are installed.${NC}"
fi

# ------------------------------------------------------------
# SECTION 2: Project structure verification
# ------------------------------------------------------------
echo -e "\n${YELLOW}[2/7] Verifying project structure...${NC}"

# Check critical files
critical_files=(
    "src/main.py"
    "setup.py"
    "README.md"
    "pyproject.toml"
    "requirements.txt"
    "docs/guides/user_guide.md"
    "docs/development/architecture.md"
    "src/core/__init__.py"
    "src/analyzers/__init__.py"
    "src/utils/__init__.py"
    "vscode-extension/extension.js"
    "vscode-extension/package.json"
)

missing_files=0
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "✓ ${GREEN}$file exists${NC}"
    else
        echo -e "✗ ${RED}$file not found${NC}"
        ((missing_files++))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo -e "\n${RED}[ERROR] Missing $missing_files critical files.${NC}"
    exit 1
else
    echo -e "${GREEN}Project structure verified successfully.${NC}"
fi

# ------------------------------------------------------------
# SECTION 3: Run unit tests
# ------------------------------------------------------------
echo -e "\n${YELLOW}[3/7] Running unit tests...${NC}"

if [ "$SKIP_TESTS" = true ]; then
    echo -e "${YELLOW}[INFO] Skipping tests as requested with --skip-tests flag.${NC}"
else
    # Check if tests directory exists
    if [ -d "tests" ]; then
        echo "Running unit tests..."
        python -m pytest tests/unit || {
            echo -e "${RED}[ERROR] Unit tests failed.${NC}"
            echo -e "${YELLOW}[TIP] You can skip tests with --skip-tests flag if needed.${NC}"
            exit 1
        }
        echo -e "${GREEN}Unit tests completed successfully.${NC}"
        
        echo "Running integration tests..."
        python -m pytest tests/integration || {
            echo -e "${YELLOW}[WARNING] Some integration tests failed.${NC}"
            echo -e "${YELLOW}Review the failures before proceeding.${NC}"
            read -p "Press Enter to continue or Ctrl+C to abort... " -r
        }
    else
        echo -e "${YELLOW}[WARNING] Tests directory not found.${NC}"
    fi
fi

# ------------------------------------------------------------
# SECTION 4: Freemium system verification
# ------------------------------------------------------------
echo -e "\n${YELLOW}[4/7] Verifying freemium system...${NC}"

if [ "$SKIP_FREEMIUM" = true ]; then
    echo -e "${YELLOW}[INFO] Skipping freemium verification as requested with --skip-freemium flag.${NC}"
else
    if [ -f "tests/run_freemium_tests.sh" ]; then
        echo "Running freemium system verification..."
        bash tests/run_freemium_tests.sh || {
            echo -e "${RED}[ERROR] Freemium system verification failed.${NC}"
            echo -e "${YELLOW}[TIP] You can skip freemium verification with --skip-freemium flag if needed.${NC}"
            exit 1
        }
        echo -e "${GREEN}Freemium system verified successfully.${NC}"
    else
        echo -e "${YELLOW}[WARNING] Freemium system verification script not found.${NC}"
    fi
fi

# ------------------------------------------------------------
# SECTION 5: Anthropic integration verification
# ------------------------------------------------------------
echo -e "\n${YELLOW}[5/7] Verifying Anthropic integration...${NC}"

if [ "$SKIP_ANTHROPIC" = true ]; then
    echo -e "${YELLOW}[INFO] Skipping Anthropic verification as requested with --skip-anthropic flag.${NC}"
else
    if [ -f "tests/run_anthropic_verification.sh" ]; then
        # Check if API key is configured
        if [ -f ".anthropic_api_key" ] || [ ! -z "$ANTHROPIC_API_KEY" ]; then
            echo "Running Anthropic integration verification..."
            bash tests/run_anthropic_verification.sh || {
                echo -e "${YELLOW}[WARNING] Anthropic integration verification failed.${NC}"
                echo -e "${YELLOW}This won't stop the process, but should be reviewed.${NC}"
            }
        else
            echo -e "${YELLOW}[WARNING] Anthropic API key not found. Skipping integration tests.${NC}"
        fi
    else
        echo -e "${YELLOW}[WARNING] Anthropic integration verification script not found.${NC}"
    fi
fi

# ------------------------------------------------------------
# SECTION 6: Distribution package generation
# ------------------------------------------------------------
echo -e "\n${YELLOW}[6/7] Generating distribution packages...${NC}"

# Clean distribution directory if it exists
if [ -d "dist" ]; then
    echo "Cleaning previous distribution directory..."
    rm -rf dist/
fi

# Build packages
echo "Generating distribution packages..."
python -m build || {
    echo -e "${RED}[ERROR] Package generation failed.${NC}"
    exit 1
}

echo -e "Verifying generated packages..."
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo -e "${GREEN}Packages generated successfully:${NC}"
    ls -la dist/
else
    echo -e "${RED}[ERROR] No packages were generated.${NC}"
    exit 1
fi

# Build VS Code Extension
echo -e "\nBuilding VS Code extension..."
if [ "$SKIP_VSCODE" = true ]; then
    echo -e "${YELLOW}[INFO] Skipping VS Code extension build as requested with --skip-vscode flag.${NC}"
else
    if [ -d "vscode-extension" ]; then
        cd vscode-extension
        echo "Installing VS Code extension dependencies..."
        npm install
        
        echo "Installing vsce globally..."
        npm install -g @vscode/vsce
        
        echo "Packaging VS Code extension..."
        if vsce package; then
            cd ..
            echo -e "${GREEN}VS Code extension package generated successfully.${NC}"
        else
            cd ..
            echo -e "${YELLOW}[WARNING] VS Code extension package generation failed.${NC}"
            echo -e "${YELLOW}This could be due to issues with the extension code. You can:${NC}"
            echo -e "${YELLOW}- Fix the extension and try again${NC}"
            echo -e "${YELLOW}- Use --skip-vscode flag to skip this step${NC}"
            read -p "Continue anyway? [y/N] " -r
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}[WARNING] VS Code extension directory not found.${NC}"
    fi
fi

# ------------------------------------------------------------
# SECTION 7: Installation verification
# ------------------------------------------------------------
echo -e "\n${YELLOW}[7/7] Verifying package installation...${NC}"

# Create virtual environment for installation testing
echo "Creating test virtual environment..."
python -m venv test_env || {
    echo -e "${RED}[ERROR] Could not create virtual environment.${NC}"
    exit 1
}

# Activate virtual environment
echo "Activating virtual environment..."
source test_env/bin/activate || {
    echo -e "${RED}[ERROR] Could not activate virtual environment.${NC}"
    exit 1
}

# Install wheel if not available
pip install wheel

# Install the generated package
echo "Installing package from wheel..."
pip install dist/*.whl || {
    echo -e "${RED}[ERROR] Package installation failed.${NC}"
    deactivate
    exit 1
}

# Verify import
echo "Verifying package import..."
PACKAGE_NAME="project_prompt"  # Update this with your actual package name
if python -c "import ${PACKAGE_NAME}; print(f'Installed version: ${${PACKAGE_NAME}.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}Package installed and verified successfully.${NC}"
else
    echo -e "${RED}[ERROR] Could not import the installed package.${NC}"
    deactivate
    exit 1
fi

# Deactivate virtual environment
deactivate

# Clean up test environment
echo "Cleaning up test environment..."
rm -rf test_env/

# ------------------------------------------------------------
# FINAL SUMMARY
# ------------------------------------------------------------
echo -e "\n${BLUE}=================================================================="
echo "     ProjectPrompt - Verification Completed Successfully"
echo "==================================================================${NC}"
echo -e "\n${GREEN}All verifications passed successfully.${NC}"
echo -e "The project is ready for publication.\n"

echo -e "${YELLOW}Final steps for publication:${NC}"
echo -e "1. Review final documentation"
echo -e "2. Update version number in pyproject.toml if necessary"
echo -e "3. Create git tag: git tag -a v1.0.0 -m \"Version 1.0.0\""
echo -e "4. Push tag: git push origin v1.0.0"
echo -e "5. Publish to PyPI: python -m twine upload dist/*"
echo -e "6. Publish VS Code extension: vsce publish -p <token> vscode-extension/*.vsix\n"

echo -e "Packages available in the dist/ directory:"
ls -la dist/
if [ -d "vscode-extension" ]; then
    echo -e "\nVS Code extension package:"
    ls -la vscode-extension/*.vsix
fi
