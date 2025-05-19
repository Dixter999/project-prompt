#!/usr/bin/env bash
# Comprehensive test suite for Anthropic markdown generation verification

# Colors for formatting
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Base directories
PROJECT_ROOT="/mnt/h/Projects/project-prompt"
TEST_DIR="${PROJECT_ROOT}/test-projects"
OUTPUT_DIR="${TEST_DIR}"

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Banner
echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD}  COMPREHENSIVE ANTHROPIC VERIFICATION SYSTEM v1.0    ${NC}"
echo -e "${BOLD}======================================================${NC}"

# Check for API key first
if [ -z "$anthropic_API" ] && [ ! -f "${PROJECT_ROOT}/.env" ] && [ ! -f "${TEST_DIR}/.env" ]; then
    echo -e "${RED}Error: No Anthropic API key found!${NC}"
    echo "Please set the anthropic_API environment variable or create a .env file."
    exit 1
fi

# Parse command line arguments
SKIP_ENV_CHECK=0
SKIP_QUICK=0
SKIP_BASIC=0
SKIP_ENHANCED=0
SKIP_COMPREHENSIVE=0
PROJECT_PATH=""
TEST_TYPES=()

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --skip-env-check)
            SKIP_ENV_CHECK=1
            shift
            ;;
        --skip-quick)
            SKIP_QUICK=1
            shift
            ;;
        --skip-basic)
            SKIP_BASIC=1
            shift
            ;;
        --skip-enhanced)
            SKIP_ENHANCED=1
            shift
            ;;
        --skip-comprehensive)
            SKIP_COMPREHENSIVE=1
            shift
            ;;
        --project)
            PROJECT_PATH="$2"
            shift
            shift
            ;;
        --types)
            shift
            while [[ $# -gt 0 ]] && [[ "$1" != --* ]]; do
                TEST_TYPES+=("$1")
                shift
            done
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-env-check       Skip environment check"
            echo "  --skip-quick           Skip quick test"
            echo "  --skip-basic           Skip basic verification"
            echo "  --skip-enhanced        Skip enhanced verification"
            echo "  --skip-comprehensive   Skip comprehensive testing"
            echo "  --project PATH         Path to existing project to analyze"
            echo "  --types TYPE1 TYPE2    Project types to test (web-project, backend-api, mobile-app, data-science, mixed)"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set default test types if not specified
if [ ${#TEST_TYPES[@]} -eq 0 ]; then
    TEST_TYPES=("web-project" "backend-api")
fi

# Track test results
ERRORS=0
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RESULTS_FILE="${OUTPUT_DIR}/test_results_${TIMESTAMP}.log"

# Function to log results
log_result() {
    echo "$1" | tee -a "${RESULTS_FILE}"
}

log_result "======================================================="
log_result "ANTHROPIC VERIFICATION TESTS - $(date)"
log_result "======================================================="

# 1. Environment check
if [ $SKIP_ENV_CHECK -eq 0 ]; then
    echo -e "\n${BOLD}Checking Environment...${NC}"
    python "${TEST_DIR}/check_anthropic_env.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Environment check failed${NC}"
        log_result "ENVIRONMENT CHECK: FAILED"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Environment check passed${NC}"
        log_result "ENVIRONMENT CHECK: PASSED"
    fi
else
    echo -e "${YELLOW}Skipping environment check${NC}"
    log_result "ENVIRONMENT CHECK: SKIPPED"
fi

# 2. Quick test
if [ $SKIP_QUICK -eq 0 ]; then
    echo -e "\n${BOLD}Running Quick Test...${NC}"
    python "${TEST_DIR}/quick_test_anthropic.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Quick test failed${NC}"
        log_result "QUICK TEST: FAILED"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Quick test passed${NC}"
        log_result "QUICK TEST: PASSED"
    fi
else
    echo -e "${YELLOW}Skipping quick test${NC}"
    log_result "QUICK TEST: SKIPPED"
fi

# 3. Basic verification
if [ $SKIP_BASIC -eq 0 ]; then
    echo -e "\n${BOLD}Running Basic Verification...${NC}"
    if [ -n "${PROJECT_PATH}" ]; then
        python "${PROJECT_ROOT}/verify_anthropic_generation.py" "${PROJECT_PATH}" -o "${OUTPUT_DIR}/basic_verification_${TIMESTAMP}.md"
    else
        python "${PROJECT_ROOT}/verify_anthropic_generation.py" -o "${OUTPUT_DIR}/basic_verification_${TIMESTAMP}.md"
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Basic verification failed${NC}"
        log_result "BASIC VERIFICATION: FAILED"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Basic verification passed${NC}"
        log_result "BASIC VERIFICATION: PASSED"
    fi
else
    echo -e "${YELLOW}Skipping basic verification${NC}"
    log_result "BASIC VERIFICATION: SKIPPED"
fi

# 4. Enhanced verification
if [ $SKIP_ENHANCED -eq 0 ]; then
    echo -e "\n${BOLD}Running Enhanced Verification...${NC}"
    
    # Construct the command with test types
    CMD="python ${TEST_DIR}/enhanced_verify_anthropic.py --project-types"
    for type in "${TEST_TYPES[@]}"; do
        CMD="$CMD $type"
    done
    
    echo "Running: $CMD"
    eval $CMD
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Enhanced verification failed${NC}"
        log_result "ENHANCED VERIFICATION: FAILED"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Enhanced verification passed${NC}"
        log_result "ENHANCED VERIFICATION: PASSED"
    fi
else
    echo -e "${YELLOW}Skipping enhanced verification${NC}"
    log_result "ENHANCED VERIFICATION: SKIPPED"
fi

# 5. Comprehensive testing
if [ $SKIP_COMPREHENSIVE -eq 0 ]; then
    echo -e "\n${BOLD}Running Comprehensive Test Suite...${NC}"
    
    if [ -n "${PROJECT_PATH}" ]; then
        python "${PROJECT_ROOT}/test_anthropic_markdown_generation.py" --skip-project-creation --project-path "${PROJECT_PATH}"
    else
        python "${PROJECT_ROOT}/test_anthropic_markdown_generation.py"
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Comprehensive testing failed${NC}"
        log_result "COMPREHENSIVE TESTING: FAILED"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ Comprehensive testing passed${NC}"
        log_result "COMPREHENSIVE TESTING: PASSED"
    fi
else
    echo -e "${YELLOW}Skipping comprehensive testing${NC}"
    log_result "COMPREHENSIVE TESTING: SKIPPED"
fi

# Summary
echo -e "\n${BOLD}======================================================${NC}"
echo -e "${BOLD}                  VERIFICATION SUMMARY                ${NC}"
echo -e "${BOLD}======================================================${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All tests completed successfully!${NC}"
    log_result "OVERALL RESULT: PASSED"
    echo -e "All output files are available in: ${OUTPUT_DIR}"
    echo -e "Log file: ${RESULTS_FILE}"
    exit 0
else
    echo -e "${RED}$ERRORS test(s) failed! Check the output above for details.${NC}"
    log_result "OVERALL RESULT: FAILED ($ERRORS errors)"
    echo -e "Output files are available in: ${OUTPUT_DIR}"
    echo -e "Log file: ${RESULTS_FILE}"
    exit 1
fi
