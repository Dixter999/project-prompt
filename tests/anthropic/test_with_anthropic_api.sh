#!/bin/bash
# Script to run tests with actual Anthropic API calls

# Terminal colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"  # No Color
BOLD="\033[1m"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Check if API key is set
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

if [ -z "$anthropic_API" ]; then
    echo -e "${RED}❌ Anthropic API key not found${NC}"
    echo "Please set the 'anthropic_API' environment variable or create a .env file"
    exit 1
fi

echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}ANTHROPIC API TESTING SUITE${NC}"
echo -e "${BOLD}=============================================${NC}"

# Temp directory for test outputs
TEMP_DIR="$SCRIPT_DIR/test_outputs"
mkdir -p "$TEMP_DIR"

# Function to run a test with timing
run_test() {
    local name=$1
    local cmd=$2
    local output_file="$TEMP_DIR/$name.log"
    
    echo -e "\n${BOLD}Running test: ${name}${NC}"
    echo "$cmd"
    
    START_TIME=$(date +%s)
    eval "$cmd" > "$output_file" 2>&1
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Test passed ($DURATION seconds)${NC}"
    else
        echo -e "${RED}❌ Test failed ($DURATION seconds)${NC}"
    fi
    
    echo -e "Log saved to: $output_file"
    
    return $EXIT_CODE
}

# Create a simple test project
echo -e "\n${BOLD}Creating test project...${NC}"
PROJECT_NAME="test_anthropic_api_$(date +%s)"
python "$SCRIPT_DIR/create_test_project.py" --type web-project --name "$PROJECT_NAME"
TEST_PROJECT_PATH="$SCRIPT_DIR/$PROJECT_NAME"

if [ ! -d "$TEST_PROJECT_PATH" ]; then
    echo -e "${RED}❌ Failed to create test project${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Created test project at: $TEST_PROJECT_PATH${NC}"

# Test direct API call with minimal input
run_test "direct_api_call" "python $SCRIPT_DIR/../analyze_with_anthropic_direct.py \"$TEST_PROJECT_PATH\" --output \"$TEMP_DIR/direct_api_output.md\""

# Test if the output contains Anthropic-generated content
if [ -f "$TEMP_DIR/direct_api_output.md" ]; then
    if grep -q "Sugerencias de Mejora (Generado por Anthropic Claude)" "$TEMP_DIR/direct_api_output.md"; then
        echo -e "${GREEN}✅ Output contains Anthropic-generated content${NC}"
        
        # Run detailed metrics analysis
        echo -e "\n${BOLD}Running advanced metrics analysis...${NC}"
        python "$SCRIPT_DIR/advanced_markdown_metrics.py" "$TEMP_DIR/direct_api_output.md" --output "$TEMP_DIR/metrics.json"
    else
        echo -e "${RED}❌ Output does not contain Anthropic-generated content${NC}"
    fi
else
    echo -e "${RED}❌ No output file was created${NC}"
fi

# Run the comprehensive verification test with a single project type
echo -e "\n${BOLD}Running comprehensive verification...${NC}"
RUN_EXPENSIVE_TESTS=1 python "$SCRIPT_DIR/test_verification_system.py" TestIntegration.test_full_verification_cycle

# Check the results of the verification
RESULTS_FILE=$(ls -t "$SCRIPT_DIR"/verification_results_*.json 2>/dev/null | head -n 1)
if [ -n "$RESULTS_FILE" ]; then
    echo -e "\n${BOLD}Latest verification results:${NC}"
    python -m json.tool "$RESULTS_FILE" | grep -E '"overall_success"|"success"|"score"|"percentage"|"reason"'
fi

# Cleanup
echo -e "\n${BOLD}Cleaning up test project...${NC}"
rm -rf "$TEST_PROJECT_PATH"
echo -e "${GREEN}✅ Test project removed${NC}"

echo -e "\n${BOLD}All test artifacts saved in: $TEMP_DIR${NC}"
echo -e "${BOLD}=============================================${NC}"
echo -e "${GREEN}✅ Testing complete${NC}"
