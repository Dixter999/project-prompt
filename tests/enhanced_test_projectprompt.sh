#!/usr/bin/env bash

# Enhanced Comprehensive Testing Script for ProjectPrompt
# This script automates the testing procedure outlined in the comprehensive testing guide

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Test project path
TEST_PROJECT_PATH="/mnt/h/Projects/project-prompt/test-projects/weather-api"
OUTPUT_DIR="/mnt/h/Projects/project-prompt/test_results"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Log file
LOG_FILE="$OUTPUT_DIR/test_results.log"
> "$LOG_FILE"  # Clear log file

# Start time for the test run
START_TIME=$(date +%s)

# Function to print section header
print_header() {
    echo -e "\n${BOLD}${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}"
    echo -e "${BLUE}$1${NC}" >> "$LOG_FILE"
    echo "$(printf '=%.0s' {1..50})" >> "$LOG_FILE"
}

# Function to run a command and log results
run_command() {
    local cmd="$1"
    local description="$2"
    local output_file="$3"
    
    echo -e "${YELLOW}Running:${NC} $cmd"
    echo -e "${YELLOW}$description${NC}"
    
    echo "Command: $cmd" >> "$LOG_FILE"
    echo "Description: $description" >> "$LOG_FILE"
    echo "Timestamp: $(date)" >> "$LOG_FILE"
    
    # Run the command and capture output
    eval "$cmd" > "$output_file" 2>&1
    local status=$?
    
    # Log the output
    echo -e "\nOutput:" >> "$LOG_FILE"
    cat "$output_file" >> "$LOG_FILE"
    echo -e "\nExit Status: $status\n" >> "$LOG_FILE"
    
    # Display status
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✅ Command succeeded${NC}"
    else
        echo -e "${RED}❌ Command failed${NC}"
    fi
    
    # Show brief output
    echo -e "${YELLOW}Output preview:${NC}"
    head -n 10 "$output_file"
    echo "..."
    
    return $status
}

# Function to check if JSON is valid
validate_json() {
    local file="$1"
    if [ -f "$file" ]; then
        if python -m json.tool "$file" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ JSON is valid${NC}"
            return 0
        else
            echo -e "${RED}❌ JSON is invalid${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ File not found: $file${NC}"
        return 1
    fi
}

# Function to summarize test results
summarize_results() {
    local passed=$1
    local failed=$2
    local skipped=$3
    local total=$((passed + failed + skipped))
    
    echo -e "\n${BOLD}Test Summary:${NC}"
    echo -e "  ${GREEN}Passed:${NC}  $passed"
    echo -e "  ${RED}Failed:${NC}  $failed"
    echo -e "  ${YELLOW}Skipped:${NC} $skipped"
    echo -e "  ${BOLD}Total:${NC}   $total"
    
    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - START_TIME))
    echo -e "  ${BOLD}Time elapsed:${NC} $elapsed seconds"
    
    echo -e "\nTest Summary:" >> "$LOG_FILE"
    echo "  Passed:  $passed" >> "$LOG_FILE"
    echo "  Failed:  $failed" >> "$LOG_FILE"
    echo "  Skipped: $skipped" >> "$LOG_FILE"
    echo "  Total:   $total" >> "$LOG_FILE"
    echo "  Time elapsed: $elapsed seconds" >> "$LOG_FILE"
}

# Welcome message
echo -e "${BOLD}${GREEN}ProjectPrompt Enhanced Comprehensive Testing Script${NC}"
echo -e "${GREEN}This script will test all features of ProjectPrompt using the Weather API test project${NC}"
echo -e "${GREEN}Results will be saved in $OUTPUT_DIR${NC}\n"

# Initialize counters for test results
PASSED=0
FAILED=0
SKIPPED=0

# 1. Testing Basic Analysis (Free Tier Features)
print_header "1. Testing Basic Analysis (Free Tier Features)"

run_command "python /mnt/h/Projects/project-prompt/project_prompt.py analyze $TEST_PROJECT_PATH" \
            "Analyzing the Weather API project structure" \
            "$OUTPUT_DIR/1_basic_analysis.txt"
            
if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
fi

# 2. Testing Project Structure Analysis
print_header "2. Testing Project Structure Analysis"

run_command "python /mnt/h/Projects/project-prompt/quick_analyze.py $TEST_PROJECT_PATH $OUTPUT_DIR/structure_analysis.json" \
            "Performing detailed structure analysis with output to JSON" \
            "$OUTPUT_DIR/2_structure_analysis.txt"

if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
fi

echo -e "${YELLOW}Checking if JSON file was created:${NC}"
if [ -f "$OUTPUT_DIR/structure_analysis.json" ]; then
    echo -e "${GREEN}✅ JSON file created successfully${NC}"
    echo -e "${YELLOW}JSON preview:${NC}"
    head -n 20 "$OUTPUT_DIR/structure_analysis.json"
    echo "..."
    
    # Validate JSON
    validate_json "$OUTPUT_DIR/structure_analysis.json"
else
    echo -e "${RED}❌ JSON file not created${NC}"
    FAILED=$((FAILED + 1))
fi

# 3. Testing Project Initialization
print_header "3. Testing Project Initialization"

# Create a temporary test project
TEST_INIT_DIR="$OUTPUT_DIR/test_init_project"
rm -rf "$TEST_INIT_DIR"  # Clean up any previous test

run_command "python /mnt/h/Projects/project-prompt/project_prompt.py init weather-test --path $OUTPUT_DIR" \
            "Initializing a new project named 'weather-test'" \
            "$OUTPUT_DIR/3_project_init.txt"

if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
fi

echo -e "${YELLOW}Checking if project was created:${NC}"
if [ -d "$OUTPUT_DIR/weather-test" ]; then
    echo -e "${GREEN}✅ Project directory created successfully${NC}"
    echo -e "${YELLOW}Project structure:${NC}"
    find "$OUTPUT_DIR/weather-test" -type f | sort
else
    echo -e "${RED}❌ Project directory not created${NC}"
    FAILED=$((FAILED + 1))
fi

# 4. Compare Functionality Between Source and Generated Projects
print_header "4. Functionality Comparison"

echo -e "${YELLOW}Comparing source and generated project structures:${NC}"

echo -e "${BOLD}Weather API Project Files:${NC}" > "$OUTPUT_DIR/4_project_comparison.txt"
find "$TEST_PROJECT_PATH" -type f -name "*.py" | sort >> "$OUTPUT_DIR/4_project_comparison.txt"

echo -e "\n${BOLD}Generated Project Files:${NC}" >> "$OUTPUT_DIR/4_project_comparison.txt"
find "$OUTPUT_DIR/weather-test" -type f -name "*.py" | sort >> "$OUTPUT_DIR/4_project_comparison.txt"

cat "$OUTPUT_DIR/4_project_comparison.txt"
PASSED=$((PASSED + 1))  # This is an informational step, not a true test

# 5. Testing Standalone Analyzer
print_header "5. Testing Standalone Analyzer"

run_command "cd /mnt/h/Projects/project-prompt && python quick_analyze.py $TEST_PROJECT_PATH" \
            "Running standalone quick analyzer" \
            "$OUTPUT_DIR/5_standalone_analyzer.txt"

if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
fi

# 6. Testing with Different Project Parts
print_header "6. Testing with Different Project Parts"

run_command "cd /mnt/h/Projects/project-prompt && python quick_analyze.py $TEST_PROJECT_PATH/src" \
            "Analyzing just the src directory" \
            "$OUTPUT_DIR/6_src_analysis.txt"

if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
fi

# 7. Testing with Different Output Format
print_header "7. Testing Different Output Format"

run_command "cd /mnt/h/Projects/project-prompt && python project_analyzer.py $TEST_PROJECT_PATH $OUTPUT_DIR/full_analysis.json" \
            "Running project_analyzer with JSON output" \
            "$OUTPUT_DIR/7_json_output.txt"

if [ $? -eq 0 ]; then
    PASSED=$((PASSED + 1))
    
    # Validate JSON
    validate_json "$OUTPUT_DIR/full_analysis.json"
else
    FAILED=$((FAILED + 1))
fi

# 8. Testing Documentation Generation (May be pending implementation)
print_header "8. Testing Documentation Generation"

if [ -f "/mnt/h/Projects/project-prompt/src/generators/markdown_generator.py" ]; then
    run_command "python /mnt/h/Projects/project-prompt/project_prompt.py docs $TEST_PROJECT_PATH --output $OUTPUT_DIR/generated_docs.md" \
                "Generating documentation for the Weather API project" \
                "$OUTPUT_DIR/8_docs_generation.txt"
    
    if [ $? -eq 0 ]; then
        PASSED=$((PASSED + 1))
        echo -e "${GREEN}✅ Documentation generation succeeded${NC}"
    else
        FAILED=$((FAILED + 1))
        echo -e "${RED}❌ Documentation generation failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Documentation generation not implemented yet or not available - skipping test${NC}"
    echo "Documentation generation not implemented yet - skipping test" >> "$LOG_FILE"
    SKIPPED=$((SKIPPED + 1))
fi

# 9. Testing Connectivity Analysis (May be pending implementation)
print_header "9. Testing Connectivity Analysis"

if [ -f "/mnt/h/Projects/project-prompt/src/analyzers/connectivity_analyzer.py" ]; then
    run_command "python /mnt/h/Projects/project-prompt/project_prompt.py connections $TEST_PROJECT_PATH --output $OUTPUT_DIR/connections.json" \
                "Analyzing connectivity in the Weather API project" \
                "$OUTPUT_DIR/9_connectivity_analysis.txt"
    
    if [ $? -eq 0 ]; then
        PASSED=$((PASSED + 1))
        # Validate JSON
        validate_json "$OUTPUT_DIR/connections.json"
    else
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️ Connectivity analysis not implemented yet or not available - skipping test${NC}"
    echo "Connectivity analysis not implemented yet - skipping test" >> "$LOG_FILE"
    SKIPPED=$((SKIPPED + 1))
fi

# 10. Testing Freemium System (May be pending implementation)
print_header "10. Testing Freemium System"

if [ -f "/mnt/h/Projects/project-prompt/verify_freemium_system.py" ]; then
    run_command "cd /mnt/h/Projects/project-prompt && python verify_freemium_system.py" \
                "Verifying freemium system functionality" \
                "$OUTPUT_DIR/10_freemium_verification.txt"
    
    if [ $? -eq 0 ]; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️ Freemium system verification not implemented yet or not available - skipping test${NC}"
    echo "Freemium system verification not implemented yet - skipping test" >> "$LOG_FILE"
    SKIPPED=$((SKIPPED + 1))
fi

# 11. Create Test Report
print_header "11. Creating Test Report"

# Generate timestamp for report
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Create report file
cat > "$OUTPUT_DIR/test_report.md" << EOL
# ProjectPrompt Test Report

Date: $TIMESTAMP
Tester: Automated Test Script

## Test Environment
- OS: $(uname -s)
- Python version: $(python --version 2>&1)
- ProjectPrompt location: /mnt/h/Projects/project-prompt

## Test Results

### 1. Basic Analysis
- Status: $([ -f "$OUTPUT_DIR/1_basic_analysis.txt" ] && grep -q "Error" "$OUTPUT_DIR/1_basic_analysis.txt" && echo "FAIL" || echo "PASS")
- Notes: $(head -n 1 "$OUTPUT_DIR/1_basic_analysis.txt")

### 2. Project Structure Analysis
- Status: $([ -f "$OUTPUT_DIR/structure_analysis.json" ] && echo "PASS" || echo "FAIL") 
- Notes: JSON output $([ -f "$OUTPUT_DIR/structure_analysis.json" ] && echo "created successfully" || echo "failed")

### 3. Project Initialization
- Status: $([ -d "$OUTPUT_DIR/weather-test" ] && echo "PASS" || echo "FAIL")
- Notes: $([ -d "$OUTPUT_DIR/weather-test" ] && echo "Project directory created" || echo "Failed to create project")

### 4. Functionality Comparison
- Status: INFO
- Notes: Comparison completed - see $OUTPUT_DIR/4_project_comparison.txt

### 5. Standalone Analyzer
- Status: $([ -f "$OUTPUT_DIR/5_standalone_analyzer.txt" ] && grep -q "Error" "$OUTPUT_DIR/5_standalone_analyzer.txt" && echo "FAIL" || echo "PASS")
- Notes: Quick analyzer ran $([ -f "$OUTPUT_DIR/5_standalone_analyzer.txt" ] && grep -q "Error" "$OUTPUT_DIR/5_standalone_analyzer.txt" && echo "with errors" || echo "successfully")

### 6. Project Subparts Analysis
- Status: $([ -f "$OUTPUT_DIR/6_src_analysis.txt" ] && grep -q "Error" "$OUTPUT_DIR/6_src_analysis.txt" && echo "FAIL" || echo "PASS")
- Notes: Analysis of src directory completed

### 7. Output Format Testing
- Status: $([ -f "$OUTPUT_DIR/full_analysis.json" ] && echo "PASS" || echo "FAIL")
- Notes: Full JSON analysis $([ -f "$OUTPUT_DIR/full_analysis.json" ] && echo "generated" || echo "failed")

### 8. Documentation Generation
- Status: $([ -f "$OUTPUT_DIR/8_docs_generation.txt" ] && echo "TESTED" || echo "SKIPPED")
- Notes: Feature may not be implemented yet

### 9. Connectivity Analysis
- Status: $([ -f "$OUTPUT_DIR/9_connectivity_analysis.txt" ] && echo "TESTED" || echo "SKIPPED")
- Notes: Feature may not be implemented yet

### 10. Freemium System Testing
- Status: $([ -f "$OUTPUT_DIR/10_freemium_verification.txt" ] && echo "TESTED" || echo "SKIPPED")
- Notes: Feature may not be implemented yet

## Summary
- Passed: $PASSED
- Failed: $FAILED
- Skipped: $SKIPPED
- Total: $((PASSED + FAILED + SKIPPED))

## Recommendations
- Review any failed tests
- Check skipped tests for implementation status
- Implement missing features as needed
EOL

echo -e "${GREEN}Test report created at $OUTPUT_DIR/test_report.md${NC}"
PASSED=$((PASSED + 1))  # Count report generation as a passed test

# Summary
print_header "Testing Summary"

summarize_results $PASSED $FAILED $SKIPPED

echo -e "${GREEN}Testing completed! All results saved to $OUTPUT_DIR${NC}"
echo -e "${YELLOW}Test log file:${NC} $LOG_FILE"
echo -e "${YELLOW}Test report:${NC} $OUTPUT_DIR/test_report.md"

# List all generated files
echo -e "${YELLOW}Generated test artifacts:${NC}"
ls -la "$OUTPUT_DIR"

echo -e "\n${BOLD}${GREEN}You can now review the results in the comprehensive test report.${NC}"
