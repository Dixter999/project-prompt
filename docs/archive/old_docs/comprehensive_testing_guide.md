# Comprehensive Testing Guide for ProjectPrompt

This guide outlines the complete testing process for ProjectPrompt using the Weather API test project. It covers testing all major features of ProjectPrompt, including project analysis, initialization, and standalone tools.

## Prerequisites

Before running the tests, ensure you have:

1. A working Python environment with all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
2. The Weather API test project in `/mnt/h/Projects/project-prompt/test-projects/weather-api`
3. Sufficient permissions to create and write files in the test directories

## Testing Setup

The testing framework uses a Weather API client sample project as its test subject. This project has:

- A well-defined structure with `src`, `tests`, and `docs` directories
- Multiple Python files with different functionalities
- A test suite
- Configuration files and documentation

A comprehensive test script (`test_projectprompt.sh`) is provided to automate all test cases and collect results.

## Test Cases

### 1. Basic Analysis (Free Tier Features)

Tests the core analysis functionality to ensure it properly identifies the project structure, languages, and files.

**Command:**
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py analyze /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected Results:**
- Should successfully scan the project
- Should identify Python as the main language
- Should count the correct number of files and directories
- Should complete without errors

### 2. Project Structure Analysis

Tests the detailed structure analysis with JSON output format.

**Command:**
```bash
python /mnt/h/Projects/project-prompt/quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api /mnt/h/Projects/project-prompt/test_results/structure_analysis.json
```

**Expected Results:**
- Should create a valid JSON file with project details
- Should include language distribution
- Should show project statistics (files, directories, etc.)
- JSON file should be readable and well-formatted

### 3. Project Initialization

Tests the initialization of a new project based on templates.

**Command:**
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py init weather-test --path /mnt/h/Projects/project-prompt/test_results
```

**Expected Results:**
- Should create a new project directory
- Should include standard directories (src, tests, docs)
- Should create basic files (README.md, setup.py)
- Should be runnable as a Python package

### 4. Functionality Comparison

Compares functionality between source and generated projects to ensure templates are working properly.

**Expected Results:**
- Source project should have more files and features
- Generated project should have the core structure intact
- Both should follow Python project standards

### 5. Standalone Analyzer Testing

Tests the quick analyzer as a standalone tool.

**Command:**
```bash
cd /mnt/h/Projects/project-prompt && python quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected Results:**
- Should provide the same analysis as the integrated command
- Should run without dependency issues
- Output should be clear and concise

### 6. Project Subparts Analysis

Tests analyzing only part of a project (the src directory).

**Command:**
```bash
cd /mnt/h/Projects/project-prompt && python quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api/src
```

**Expected Results:**
- Should correctly analyze the subdirectory
- Should show fewer files than the full project
- Should identify Python as the main language

### 7. Output Format Testing

Tests the project_analyzer tool with JSON output.

**Command:**
```bash
cd /mnt/h/Projects/project-prompt && python project_analyzer.py /mnt/h/Projects/project-prompt/test-projects/weather-api /mnt/h/Projects/project-prompt/test_results/full_analysis.json
```

**Expected Results:**
- Should create a detailed JSON file
- JSON format should be valid and well-structured
- Should include more details than the quick analyzer

## Advanced Test Cases (Pending Implementation)

### 8. Documentation Generation

Tests the documentation generation feature (when implemented).

**Command:**
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py docs /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected Results:**
- Should generate project documentation in a specified format
- Should identify key modules and functions
- Should include class information and method documentation

### 9. Connectivity Analysis

Tests the connections analysis feature (when implemented).

**Command:**
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py connections /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected Results:**
- Should identify module dependencies
- Should show function calls between modules
- Should create a connectivity graph of the project

### 10. Freemium System Testing

Tests the freemium system feature to ensure it correctly restricts premium features.

**Command:**
```bash
cd /mnt/h/Projects/project-prompt && python verify_freemium_system.py
```

**Expected Results:**
- Should identify free vs premium features
- Should restrict access to premium features without credentials
- Should allow access to free features regardless of authentication

## Running the Test Script

The complete test suite can be run using the provided test script:

```bash
cd /mnt/h/Projects/project-prompt
./test_projectprompt.sh
```

This will execute all test cases in sequence and save the results in the `/mnt/h/Projects/project-prompt/test_results` directory.

## Reviewing Test Results

Test results are saved in the `/mnt/h/Projects/project-prompt/test_results` directory. Each test produces:

1. A text file with the command output
2. JSON files for tests that generate structured output
3. A log file with detailed execution information

You should review:
- Command success/failure status
- Output format and content
- Generated project structures
- Error messages (if any)

## Test Report Template

When conducting tests, use this template to document your findings:

```
# ProjectPrompt Test Report

Date: YYYY-MM-DD
Tester: [Your Name]

## Test Environment
- OS: 
- Python version:
- ProjectPrompt version:

## Test Results

### 1. Basic Analysis
- Status: [PASS/FAIL]
- Notes: 

### 2. Project Structure Analysis
- Status: [PASS/FAIL]
- Notes: 

[Continue for all test cases...]

## Issues Found
1. [Description of issue 1]
2. [Description of issue 2]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

## Troubleshooting Common Issues

### Analysis fails with "No such file or directory"
- Ensure the test project path is correct
- Check file permissions

### Empty JSON output
- Check if the analyzer completed successfully
- Verify the output path is writable

### Missing dependencies
- Install required packages using `pip install -r requirements.txt`

### Script permission denied
- Make the script executable: `chmod +x test_projectprompt.sh`
