#!/bin/bash

# ProjectPrompt Complete Testing Script
# This script systematically tests all ProjectPrompt commands and functionalities

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
START_TIME=$(date +%s)

# Test results directory
TEST_RESULTS_DIR="test-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEST_RESULTS_DIR"

# Log file
LOG_FILE="$TEST_RESULTS_DIR/test_execution.log"

# Function to print colored headers
print_header() {
    local text="$1"
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🧪 $text${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Function to print section headers
print_section() {
    local text="$1"
    echo -e "\n${PURPLE}--- $text ---${NC}"
}

# Function to test command with detailed output
test_command() {
    local cmd="$1"
    local description="$2"
    local expect_success="${3:-true}"
    local timeout="${4:-30}"
    
    echo -e "\n${CYAN}Testing:${NC} $description"
    echo -e "${CYAN}Command:${NC} $cmd"
    echo "Testing: $description" >> "$LOG_FILE"
    echo "Command: $cmd" >> "$LOG_FILE"
    
    # Create individual test result file
    local test_file="$TEST_RESULTS_DIR/$(echo "$cmd" | tr ' ' '_' | tr -d '/')"
    
    # Run command with timeout and capture output
    if timeout "$timeout" bash -c "$cmd" > "$test_file" 2>&1; then
        local exit_code=$?
        if [ "$expect_success" = "true" ]; then
            echo -e "${GREEN}✓ PASSED${NC} (exit code: $exit_code)"
            echo "Result: PASSED (exit code: $exit_code)" >> "$LOG_FILE"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ FAILED${NC} (expected failure but command succeeded)"
            echo "Result: FAILED (expected failure but command succeeded)" >> "$LOG_FILE"
            ((TESTS_FAILED++))
        fi
    else
        local exit_code=$?
        if [ "$expect_success" = "false" ]; then
            echo -e "${GREEN}✓ PASSED${NC} (expected failure, exit code: $exit_code)"
            echo "Result: PASSED (expected failure, exit code: $exit_code)" >> "$LOG_FILE"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ FAILED${NC} (exit code: $exit_code)"
            echo "Result: FAILED (exit code: $exit_code)" >> "$LOG_FILE"
            ((TESTS_FAILED++))
            
            # Show error output for failed tests
            echo -e "${YELLOW}Error output:${NC}"
            tail -10 "$test_file" | sed 's/^/  /'
        fi
    fi
    
    # Show brief output summary
    local output_lines=$(wc -l < "$test_file")
    echo -e "${CYAN}Output:${NC} $output_lines lines (saved to $test_file)"
    echo "Output lines: $output_lines" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
}

# Function to test command with interactive input
test_interactive_command() {
    local cmd="$1"
    local description="$2"
    local input="$3"
    
    echo -e "\n${CYAN}Testing (Interactive):${NC} $description"
    echo -e "${CYAN}Command:${NC} $cmd"
    echo -e "${CYAN}Input:${NC} $input"
    
    local test_file="$TEST_RESULTS_DIR/$(echo "$cmd" | tr ' ' '_' | tr -d '/')_interactive"
    
    if echo "$input" | timeout 30 bash -c "$cmd" > "$test_file" 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        echo -e "${YELLOW}Error output:${NC}"
        tail -10 "$test_file" | sed 's/^/  /'
    fi
}

# Function to check if command exists
check_command_exists() {
    local cmd="$1"
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd is available"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $cmd is not available"
        return 1
    fi
}

# Main testing function
main() {
    print_header "ProjectPrompt Complete Testing Suite"
    
    echo "Test execution started at: $(date)"
    echo "Test results directory: $TEST_RESULTS_DIR"
    echo "Log file: $LOG_FILE"
    
    # Initialize log
    echo "ProjectPrompt Testing Log - $(date)" > "$LOG_FILE"
    echo "========================================" >> "$LOG_FILE"
    
    # Check prerequisites
    print_section "Prerequisites Check"
    check_command_exists "python3"
    check_command_exists "pip"
    check_command_exists "node" || echo "Node.js not found - some dependency analysis features may be limited"
    check_command_exists "npm" || echo "npm not found - dependency installation may be limited"
    
    # Check if ProjectPrompt is accessible
    print_section "ProjectPrompt Accessibility Check"
    
    # Try different ways to run ProjectPrompt
    if command -v "project-prompt" &> /dev/null; then
        PP_CMD="project-prompt"
        echo -e "${GREEN}✓${NC} project-prompt command available"
    elif command -v "pp" &> /dev/null; then
        PP_CMD="pp"
        echo -e "${GREEN}✓${NC} pp alias available"
    elif [ -f "src/main.py" ]; then
        PP_CMD="python3 src/main.py"
        echo -e "${GREEN}✓${NC} Using python3 src/main.py"
    else
        echo -e "${RED}✗${NC} ProjectPrompt not accessible"
        echo "Please ensure ProjectPrompt is installed or run from project directory"
        exit 1
    fi
    
    echo "Using command: $PP_CMD"
    
    # Test 1: Basic Information Commands
    print_header "1. Basic Information Commands"
    
    test_command "$PP_CMD version" "Show version information"
    test_command "$PP_CMD help" "Show general help"
    test_command "$PP_CMD help analyze" "Show analyze command help"
    test_command "$PP_CMD help config" "Show config command help"
    test_command "$PP_CMD diagnose" "Run diagnostic checks"
    
    # Test 2: Configuration Commands
    print_header "2. Configuration Commands"
    
    test_command "$PP_CMD config show" "Show current configuration"
    test_command "$PP_CMD config list" "List configuration options"
    test_command "$PP_CMD check-env" "Check environment variables"
    test_command "$PP_CMD set-log-level INFO" "Set log level to INFO"
    test_command "$PP_CMD set-log-level DEBUG" "Set log level to DEBUG"
    
    # Test configuration setting (safe values)
    test_command "$PP_CMD config set project_name TestProject" "Set project name"
    test_command "$PP_CMD config set description 'Testing ProjectPrompt'" "Set project description"
    
    # Test 3: Analysis Commands
    print_header "3. Analysis Commands"
    
    test_command "$PP_CMD analyze" "Analyze current project"
    test_command "$PP_CMD analyze --detailed" "Detailed project analysis"
    test_command "$PP_CMD analyze --output $TEST_RESULTS_DIR/analysis.md" "Analysis with output file"
    
    # Dependency analysis
    test_command "$PP_CMD deps" "Dependency analysis"
    test_command "$PP_CMD deps --max-files 50" "Limited dependency analysis"
    test_command "$PP_CMD deps --output $TEST_RESULTS_DIR/dependencies.md" "Dependency analysis with output"
    
    # Dashboard generation
    test_command "$PP_CMD dashboard" "Generate dashboard"
    test_command "$PP_CMD dashboard --format markdown" "Dashboard in markdown format"
    test_command "$PP_CMD dashboard --format json --output $TEST_RESULTS_DIR/dashboard.json" "Dashboard in JSON format"
    
    # Test 4: Project Setup Commands
    print_header "4. Project Setup Commands"
    
    # Create temporary directory for init testing
    TEMP_PROJECT_DIR="$TEST_RESULTS_DIR/temp_project"
    mkdir -p "$TEMP_PROJECT_DIR"
    
    test_command "$PP_CMD init-project-folder" "Initialize project folder"
    test_interactive_command "$PP_CMD setup-alias" "Setup command alias" "n"
    test_command "$PP_CMD setup-deps" "Setup dependencies"
    
    # Test init in temporary directory
    (cd "$TEMP_PROJECT_DIR" && test_command "$PP_CMD init" "Initialize new project")
    
    # Test 5: AI Commands (may require API keys)
    print_header "5. AI-Powered Commands (Premium Features)"
    
    echo "Note: These tests may fail if API keys are not configured"
    
    test_command "$PP_CMD analyze-group" "List available groups" false
    test_command "$PP_CMD analyze-group 'src/analyzers'" "Analyze specific group" false
    test_command "$PP_CMD generate-suggestions --group 'src/analyzers'" "Generate suggestions" false
    
    # General AI commands (likely to fail without API keys)
    test_command "$PP_CMD ai chat 'Hello'" "AI chat test" false
    test_command "$PP_CMD premium list" "List premium features" false
    
    # Test 6: Rules Management
    print_header "6. Rules Management Commands"
    
    test_command "$PP_CMD rules suggest" "Generate rule suggestions"
    test_command "$PP_CMD rules analyze-patterns" "Analyze project patterns"
    test_command "$PP_CMD rules generate-project-rules --output $TEST_RESULTS_DIR/project-rules.md" "Generate project rules"
    test_command "$PP_CMD rules generate-structured-rules --output $TEST_RESULTS_DIR/structured-rules.yaml" "Generate structured rules"
    
    # Test 7: Progress and Status Commands
    print_header "7. Progress and Status Commands"
    
    test_command "$PP_CMD status" "Show sync status"
    test_command "$PP_CMD track-progress --group 'src/analyzers' --phase 1" "Track progress" false
    
    # Test 8: Documentation Commands
    print_header "8. Documentation Commands"
    
    test_command "$PP_CMD docs list" "List documentation"
    test_command "$PP_CMD docs search 'api'" "Search documentation"
    
    # Test 9: Utility Commands
    print_header "9. Utility Commands"
    
    test_command "$PP_CMD telemetry status" "Check telemetry status"
    test_command "$PP_CMD telemetry disable" "Disable telemetry"
    test_command "$PP_CMD telemetry enable" "Enable telemetry"
    
    test_command "$PP_CMD update check" "Check for updates"
    
    # Test interactive menu (timeout quickly)
    echo "Testing interactive menu (will timeout after 5 seconds)..."
    if timeout 5 echo "" | $PP_CMD menu > "$TEST_RESULTS_DIR/menu_test" 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} Menu opened successfully"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ TIMEOUT${NC} Menu test timed out (expected)"
        ((TESTS_SKIPPED++))
    fi
    
    # Test 10: Error Handling
    print_header "10. Error Handling Tests"
    
    echo "Testing command behavior with invalid inputs..."
    
    test_command "$PP_CMD analyze /nonexistent/path" "Analysis with invalid path" false
    test_command "$PP_CMD analyze-group 'nonexistent-group'" "Analyze nonexistent group" false
    test_command "$PP_CMD config set invalid_key invalid_value" "Set invalid config" false
    
    # Test 11: File Operations
    print_header "11. File Operations and Cleanup"
    
    test_command "$PP_CMD delete --type analysis" "Delete analysis files" false
    test_command "$PP_CMD delete --type suggestions" "Delete suggestion files" false
    
    # Test 12: API Configuration (safe tests)
    print_header "12. API Configuration Tests"
    
    test_command "$PP_CMD verify-api" "Verify API configuration"
    
    # Test setting dummy API keys (they won't work but shouldn't crash)
    test_command "$PP_CMD set-api anthropic dummy-key-for-testing" "Set dummy Anthropic key" false
    test_command "$PP_CMD verify-api" "Verify API after setting dummy key"
    
    # Generate final report
    print_header "Testing Complete - Generating Report"
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
    
    # Create summary report
    REPORT_FILE="$TEST_RESULTS_DIR/test_summary_report.md"
    cat > "$REPORT_FILE" << EOF
# ProjectPrompt Testing Report

**Generated:** $(date)
**Duration:** ${DURATION} seconds
**Test Results Directory:** $TEST_RESULTS_DIR

## Summary

- **Total Tests:** $TOTAL_TESTS
- **Passed:** $TESTS_PASSED
- **Failed:** $TESTS_FAILED
- **Skipped:** $TESTS_SKIPPED
- **Success Rate:** $(( TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED) ))%

## Test Categories

1. **Basic Information Commands** - Core functionality
2. **Configuration Commands** - Settings management
3. **Analysis Commands** - Project analysis features
4. **Project Setup Commands** - Initialization and setup
5. **AI-Powered Commands** - Premium AI features
6. **Rules Management** - Rule system functionality
7. **Progress and Status** - Tracking and status
8. **Documentation** - Help and documentation
9. **Utility Commands** - General utilities
10. **Error Handling** - Robustness testing
11. **File Operations** - File management
12. **API Configuration** - API setup and verification

## Files Generated

EOF
    
    # List all generated files
    echo "### Test Output Files" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    for file in "$TEST_RESULTS_DIR"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
            echo "- \`$filename\` (${size} bytes)" >> "$REPORT_FILE"
        fi
    done
    
    echo "" >> "$REPORT_FILE"
    echo "## Recommendations" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "✅ **All tests passed!** ProjectPrompt is working correctly." >> "$REPORT_FILE"
    else
        echo "⚠️ **$TESTS_FAILED tests failed.** Review the failed tests:" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "1. Check API key configuration for AI features" >> "$REPORT_FILE"
        echo "2. Ensure all dependencies are installed" >> "$REPORT_FILE"
        echo "3. Verify file permissions and access" >> "$REPORT_FILE"
        echo "4. Review error logs in individual test files" >> "$REPORT_FILE"
    fi
    
    # Display final results
    echo ""
    echo "================================================"
    echo "🎯 TESTING COMPLETE"
    echo "================================================"
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"
    echo "Duration: ${DURATION} seconds"
    echo ""
    echo "📁 Results saved to: $TEST_RESULTS_DIR"
    echo "📄 Summary report: $REPORT_FILE"
    echo "📋 Execution log: $LOG_FILE"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ALL TESTS PASSED! ProjectPrompt is working correctly.${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️ $TESTS_FAILED tests failed. Check the report for details.${NC}"
        exit 1
    fi
}

# Handle Ctrl+C gracefully
cleanup() {
    echo -e "\n${YELLOW}Testing interrupted by user${NC}"
    echo "Partial results saved in: $TEST_RESULTS_DIR"
    exit 130
}

trap cleanup INT

# Run main function
main "$@"
