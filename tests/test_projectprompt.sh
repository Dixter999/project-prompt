#!/usr/bin/env bash

# Comprehensive Testing Script for ProjectPrompt
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

# Welcome message
echo -e "${BOLD}${GREEN}ProjectPrompt Comprehensive Testing Script${NC}"
echo -e "${GREEN}This script will test all features of ProjectPrompt using the Weather API test project${NC}"
echo -e "${GREEN}Results will be saved in $OUTPUT_DIR${NC}\n"

# 1. Testing Basic Analysis (Free Tier Features)
print_header "1. Testing Basic Analysis (Free Tier Features)"

run_command "python /mnt/h/Projects/project-prompt/project_prompt.py analyze $TEST_PROJECT_PATH" \
            "Analyzing the Weather API project structure" \
            "$OUTPUT_DIR/1_basic_analysis.txt"

# 2. Testing Project Structure Analysis
print_header "2. Testing Project Structure Analysis"

run_command "python /mnt/h/Projects/project-prompt/quick_analyze.py $TEST_PROJECT_PATH $OUTPUT_DIR/structure_analysis.json" \
            "Performing detailed structure analysis with output to JSON" \
            "$OUTPUT_DIR/2_structure_analysis.txt"

echo -e "${YELLOW}Checking if JSON file was created:${NC}"
if [ -f "$OUTPUT_DIR/structure_analysis.json" ]; then
    echo -e "${GREEN}✅ JSON file created successfully${NC}"
    echo -e "${YELLOW}JSON preview:${NC}"
    head -n 20 "$OUTPUT_DIR/structure_analysis.json"
    echo "..."
else
    echo -e "${RED}❌ JSON file not created${NC}"
fi

# 3. Testing Project Initialization
print_header "3. Testing Project Initialization"

# Create a temporary test project
TEST_INIT_DIR="$OUTPUT_DIR/test_init_project"
rm -rf "$TEST_INIT_DIR"  # Clean up any previous test

run_command "python /mnt/h/Projects/project-prompt/project_prompt.py init weather-test --path $OUTPUT_DIR" \
            "Initializing a new project named 'weather-test'" \
            "$OUTPUT_DIR/3_project_init.txt"

echo -e "${YELLOW}Checking if project was created:${NC}"
if [ -d "$OUTPUT_DIR/weather-test" ]; then
    echo -e "${GREEN}✅ Project directory created successfully${NC}"
    echo -e "${YELLOW}Project structure:${NC}"
    find "$OUTPUT_DIR/weather-test" -type f | sort
else
    echo -e "${RED}❌ Project directory not created${NC}"
fi

# 4. Compare Functionality Between Source and Generated Projects
print_header "4. Functionality Comparison"

echo -e "${YELLOW}Comparing source and generated project structures:${NC}"

echo -e "${BOLD}Weather API Project Files:${NC}" > "$OUTPUT_DIR/4_project_comparison.txt"
find "$TEST_PROJECT_PATH" -type f -name "*.py" | sort >> "$OUTPUT_DIR/4_project_comparison.txt"

echo -e "\n${BOLD}Generated Project Files:${NC}" >> "$OUTPUT_DIR/4_project_comparison.txt"
find "$OUTPUT_DIR/weather-test" -type f -name "*.py" | sort >> "$OUTPUT_DIR/4_project_comparison.txt"

cat "$OUTPUT_DIR/4_project_comparison.txt"

# 5. Testing Standalone Analyzer
print_header "5. Testing Standalone Analyzer"

run_command "cd /mnt/h/Projects/project-prompt && python quick_analyze.py $TEST_PROJECT_PATH" \
            "Running standalone quick analyzer" \
            "$OUTPUT_DIR/5_standalone_analyzer.txt"

# 6. Testing with Different Project Parts
print_header "6. Testing with Different Project Parts"

run_command "cd /mnt/h/Projects/project-prompt && python quick_analyze.py $TEST_PROJECT_PATH/src" \
            "Analyzing just the src directory" \
            "$OUTPUT_DIR/6_src_analysis.txt"

# 7. Testing with Different Output Format
print_header "7. Testing Different Output Format"

run_command "cd /mnt/h/Projects/project-prompt && python project_analyzer.py $TEST_PROJECT_PATH $OUTPUT_DIR/full_analysis.json" \
            "Running project_analyzer with JSON output" \
            "$OUTPUT_DIR/7_json_output.txt"

# Summary
print_header "Testing Summary"

echo -e "${GREEN}Testing completed! All results saved to $OUTPUT_DIR${NC}"
echo -e "${YELLOW}Test log file:${NC} $LOG_FILE"

# List all generated files
echo -e "${YELLOW}Generated test artifacts:${NC}"
ls -la "$OUTPUT_DIR"

echo -e "\n${BOLD}${GREEN}You can now review the results and see if ProjectPrompt correctly analyzed the Weather API project.${NC}"
