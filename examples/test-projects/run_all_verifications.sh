#!/bin/bash
# Script for verifying the Anthropic markdown generation

# Set output directory
OUTPUT_DIR="/mnt/h/Projects/project-prompt/test-projects"
mkdir -p "$OUTPUT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Banner
echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD}  ANTHROPIC MARKDOWN GENERATION VERIFICATION SUITE    ${NC}"
echo -e "${BOLD}======================================================${NC}"

# Check for API key first
if [ -z "$anthropic_API" ] && [ ! -f .env ] && [ ! -f "$OUTPUT_DIR/.env" ]; then
    echo -e "${RED}Error: No Anthropic API key found!${NC}"
    echo "Please set the anthropic_API environment variable or create a .env file."
    exit 1
fi

# Parse arguments
SKIP_QUICK=0
SKIP_FULL=0
PROJECT_PATH="."

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --skip-quick)
            SKIP_QUICK=1
            shift
            ;;
        --skip-full)
            SKIP_FULL=1
            shift
            ;;
        --project)
            PROJECT_PATH="$2"
            shift
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--skip-quick] [--skip-full] [--project PATH]"
            exit 1
            ;;
    esac
done

# Run tests
ERRORS=0

# 1. Quick test
if [ $SKIP_QUICK -eq 0 ]; then
    echo -e "\n${BOLD}Running Quick Test...${NC}"
    python "$OUTPUT_DIR/quick_test_anthropic.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Quick test failed${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Quick test passed${NC}"
    fi
else
    echo -e "\n${YELLOW}Skipping quick test as requested${NC}"
fi

# 2. Basic verification
echo -e "\n${BOLD}Running Basic Verification...${NC}"
python verify_anthropic_generation.py "$PROJECT_PATH" -o "$OUTPUT_DIR/basic_verification_result.md"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Basic verification failed${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✓ Basic verification passed${NC}"
fi

# 3. Full test suite
if [ $SKIP_FULL -eq 0 ]; then
    echo -e "\n${BOLD}Running Comprehensive Test Suite...${NC}"
    python test_anthropic_markdown_generation.py --skip-project-creation --project-path "$PROJECT_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Comprehensive test failed${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Comprehensive test passed${NC}"
    fi
else
    echo -e "\n${YELLOW}Skipping comprehensive test as requested${NC}"
fi

# Summary
echo -e "\n${BOLD}======================================================${NC}"
echo -e "${BOLD}                  VERIFICATION SUMMARY                ${NC}"
echo -e "${BOLD}======================================================${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    echo -e "All output files are available in: ${OUTPUT_DIR}"
    exit 0
else
    echo -e "${RED}$ERRORS test(s) failed! Check the output above for details.${NC}"
    echo -e "Output files are available in: ${OUTPUT_DIR}"
    exit 1
fi
