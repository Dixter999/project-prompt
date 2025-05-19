#!/bin/bash
# Script to integrate the Anthropic verification into CI/CD pipeline
# This script is designed to be run in a CI environment like GitHub Actions

set -e  # Exit immediately if a command exits with non-zero status

# Terminal colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"  # No Color
BOLD="\033[1m"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_DIR/test-projects"

# Parse arguments
SKIP_API_TESTS=0
VERBOSITY=1
PROJECT_TYPES=("web-project")

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --skip-api-tests)
            SKIP_API_TESTS=1
            shift
            ;;
        --project-types)
            shift
            PROJECT_TYPES=()
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                PROJECT_TYPES+=("$1")
                shift
            done
            ;;
        --verbose)
            VERBOSITY=2
            shift
            ;;
        --quiet)
            VERBOSITY=0
            shift
            ;;
        *)  # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if running in CI
if [ -n "$CI" ]; then
    echo "Running in CI environment"
    
    # Check if API key is set as a secret
    if [ -z "$anthropic_API" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${RED}❌ Anthropic API key not found${NC}"
        echo "Please set the 'anthropic_API' or 'ANTHROPIC_API_KEY' environment variable in your CI secrets"
        exit 1
    fi
    
    # Use ANTHROPIC_API_KEY if anthropic_API is not set
    if [ -z "$anthropic_API" ] && [ -n "$ANTHROPIC_API_KEY" ]; then
        export anthropic_API="$ANTHROPIC_API_KEY"
    fi
else
    echo "Running in local environment"
    
    # Check for API key in environment
    if [ -z "$anthropic_API" ]; then
        # Try to load from .env file
        if [ -f "$PROJECT_DIR/.env" ]; then
            source "$PROJECT_DIR/.env"
        elif [ -f "$TEST_DIR/.env" ]; then
            source "$TEST_DIR/.env"
        fi
        
        # Check if we got the API key
        if [ -z "$anthropic_API" ]; then
            echo -e "${RED}❌ Anthropic API key not found${NC}"
            echo "Please set the 'anthropic_API' environment variable or create a .env file"
            echo "Continuing with mock tests only..."
            SKIP_API_TESTS=1
        fi
    fi
fi

echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}ANTHROPIC VERIFICATION CI/CD INTEGRATION${NC}"
echo -e "${BOLD}=============================================${NC}"

# Create output directory for test results
TIMESTAMP=$(date +%Y%m%d%H%M%S)
OUTPUT_DIR="$TEST_DIR/ci_results_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"
echo "Test results will be saved to: $OUTPUT_DIR"

# Log configuration
echo -e "\n${BOLD}Configuration:${NC}"
echo "- Skip API tests: $SKIP_API_TESTS"
echo "- Project types: ${PROJECT_TYPES[*]}"
echo "- Verbosity: $VERBOSITY"

# Function to run a test with error handling
run_test() {
    local name=$1
    local cmd=$2
    local output_file="$OUTPUT_DIR/${name}.log"
    local exit_code=0
    
    echo -e "\n${BOLD}Running test: ${name}${NC}"
    if [ $VERBOSITY -ge 1 ]; then
        echo "$cmd"
    fi
    
    # Run the command and capture exit code
    if [ $VERBOSITY -ge 2 ]; then
        # Run with output visible
        eval "$cmd" 2>&1 | tee "$output_file" || exit_code=$?
    else
        # Run silently and log output
        eval "$cmd" > "$output_file" 2>&1 || exit_code=$?
    fi
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ Test passed${NC}"
        if [ $VERBOSITY -ge 1 ]; then
            echo -e "Log saved to: $output_file"
        fi
    else
        echo -e "${RED}❌ Test failed with exit code: $exit_code${NC}"
        echo -e "Log saved to: $output_file"
        
        # In CI, show the last few lines of the error
        if [ -n "$CI" ] || [ $VERBOSITY -ge 1 ]; then
            echo -e "\n${YELLOW}Error output:${NC}"
            tail -n 20 "$output_file"
        fi
    fi
    
    # Return the original exit code
    return $exit_code
}

# Check environment
echo -e "\n${BOLD}Checking environment:${NC}"
run_test "environment_check" "python $TEST_DIR/check_anthropic_env.py" || {
    echo -e "${YELLOW}⚠️ Environment check failed, but continuing with limited tests${NC}"
}

# Run unit tests
echo -e "\n${BOLD}Running unit tests:${NC}"
run_test "unit_tests" "python $TEST_DIR/test_verification_system.py" || {
    echo -e "${RED}❌ Unit tests failed${NC}"
    exit 1
}

# Run API tests if not skipped
if [ $SKIP_API_TESTS -eq 0 ]; then
    echo -e "\n${BOLD}Running API integration tests:${NC}"
    
    # Build project types string for command
    PROJECT_TYPES_STR=""
    for type in "${PROJECT_TYPES[@]}"; do
        PROJECT_TYPES_STR="$PROJECT_TYPES_STR $type"
    done
    
    # Run enhanced verification with specified project types
    run_test "enhanced_verification" "python $TEST_DIR/enhanced_verify_anthropic.py --project-types$PROJECT_TYPES_STR" || {
        echo -e "${RED}❌ API tests failed${NC}"
        
        # Save test artifacts in CI
        if [ -n "$CI" ]; then
            echo "Test artifacts saved to: $OUTPUT_DIR"
            
            # If in GitHub Actions, upload artifacts
            if [ -n "$GITHUB_ACTIONS" ]; then
                echo "::set-output name=test_artifacts::$OUTPUT_DIR"
            fi
        fi
        
        exit 1
    }
else
    echo -e "\n${YELLOW}⚠️ Skipping API tests as requested${NC}"
fi

# Run advanced metrics test on a sample file, if available
SAMPLE_FILES=($(find "$TEST_DIR" -name "anthropic_analysis_*.md" -type f | head -n 1))
if [ ${#SAMPLE_FILES[@]} -gt 0 ] && [ -f "${SAMPLE_FILES[0]}" ]; then
    echo -e "\n${BOLD}Running advanced metrics analysis:${NC}"
    run_test "advanced_metrics" "python $TEST_DIR/advanced_markdown_metrics.py \"${SAMPLE_FILES[0]}\" --output \"$OUTPUT_DIR/metrics.json\"" || {
        echo -e "${YELLOW}⚠️ Advanced metrics analysis failed, but continuing${NC}"
    }
fi

# Generate summary report
echo -e "\n${BOLD}Generating verification summary:${NC}"
cat > "$OUTPUT_DIR/summary.md" << EOF
# Anthropic Verification Summary

- **Date:** $(date)
- **Project types tested:** ${PROJECT_TYPES[*]}
- **API tests enabled:** $([ $SKIP_API_TESTS -eq 0 ] && echo "Yes" || echo "No")

## Test Results

| Test | Status |
|------|--------|
EOF

for log_file in "$OUTPUT_DIR"/*.log; do
    test_name=$(basename "$log_file" .log)
    if grep -q "Test passed" "$log_file"; then
        status="✅ Passed"
    else
        status="❌ Failed"
    fi
    echo "| $test_name | $status |" >> "$OUTPUT_DIR/summary.md"
done

# Add metrics summary if available
if [ -f "$OUTPUT_DIR/metrics.json" ]; then
    echo -e "\n## Metrics Summary\n" >> "$OUTPUT_DIR/summary.md"
    echo "See [metrics.json](./metrics.json) for detailed metrics." >> "$OUTPUT_DIR/summary.md"
    
    # Extract some key metrics
    if command -v jq &> /dev/null; then
        quality_score=$(jq -r '.quality_score.percentage // "N/A"' "$OUTPUT_DIR/metrics.json")
        rating=$(jq -r '.quality_score.rating // "N/A"' "$OUTPUT_DIR/metrics.json")
        
        echo -e "\n**Quality Score:** $quality_score%" >> "$OUTPUT_DIR/summary.md"
        echo -e "\n**Rating:** $rating" >> "$OUTPUT_DIR/summary.md"
    fi
fi

echo -e "${GREEN}✅ Summary report generated: $OUTPUT_DIR/summary.md${NC}"

# Final status
echo -e "\n${BOLD}=============================================${NC}"
echo -e "${GREEN}✅ Verification completed successfully${NC}"
echo -e "${BOLD}=============================================${NC}"

# In CI, set output variables
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "::set-output name=verification_status::success"
    echo "::set-output name=summary_path::$OUTPUT_DIR/summary.md"
fi

exit 0
