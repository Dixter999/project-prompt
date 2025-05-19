#!/usr/bin/env bash

# run_complete_test.sh
# Script for running a complete test of ProjectPrompt and generating a report

echo -e "\033[1;32mProjectPrompt Complete Testing Suite\033[0m"
echo "This script will run all tests and generate a comprehensive test report"
echo ""

# Define paths
PROJECT_ROOT="/mnt/h/Projects/project-prompt"
TEST_SCRIPT="$PROJECT_ROOT/enhanced_test_projectprompt.sh"
TEST_RESULTS_DIR="$PROJECT_ROOT/test_results"
REPORT_TEMPLATE="$PROJECT_ROOT/docs/test_report_template.md"
FINAL_REPORT="$TEST_RESULTS_DIR/complete_test_report_$(date +%Y%m%d_%H%M%S).md"

# Create output directory if it doesn't exist
mkdir -p "$TEST_RESULTS_DIR"

# Check if test script exists
if [ ! -f "$TEST_SCRIPT" ]; then
    echo -e "\033[1;31mError: Test script not found at $TEST_SCRIPT\033[0m"
    exit 1
fi

# Make the test script executable if it's not already
chmod +x "$TEST_SCRIPT"

# Run the enhanced test script
echo -e "\033[1;34mRunning comprehensive tests...\033[0m"
"$TEST_SCRIPT"
TEST_STATUS=$?

# Generate timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Copy the template to create the final report
cp "$REPORT_TEMPLATE" "$FINAL_REPORT"

# Update the report template with actual values
sed -i "s/\[DATE\]/$TIMESTAMP/g" "$FINAL_REPORT"
sed -i "s/\[NAME\]/Automated Test Runner/g" "$FINAL_REPORT"
sed -i "s/\[OPERATING SYSTEM\]/$(uname -s) $(uname -r)/g" "$FINAL_REPORT"
sed -i "s/\[VERSION\]/$(python --version 2>&1)/g" "$FINAL_REPORT"
sed -i "s/\[VERSION\]/$(grep -i version "$PROJECT_ROOT/src/__init__.py" | cut -d '"' -f 2)/g" "$FINAL_REPORT"

echo -e "\033[1;32mTesting complete!\033[0m"
echo "Overall test status: $([ $TEST_STATUS -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "Complete test report generated at: $FINAL_REPORT"
echo ""
echo "Next steps:"
echo "1. Review the test report"
echo "2. Check individual test outputs in $TEST_RESULTS_DIR"
echo "3. Fix any issues identified in the tests"
echo ""
echo "For more information, see the testing guide at: $PROJECT_ROOT/docs/testing_guide.md"

exit $TEST_STATUS
