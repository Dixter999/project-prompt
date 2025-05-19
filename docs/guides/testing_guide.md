# ProjectPrompt Testing Guide

## Introduction

This document provides a comprehensive guide for testing ProjectPrompt, a tool for analyzing and documenting projects. The testing process uses a Weather API client project as a sample test subject, covering all major features of ProjectPrompt.

## Prerequisites

Before beginning testing, ensure you have:

1. A working Python environment (3.8+) with all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Access to the Weather API test project in `/mnt/h/Projects/project-prompt/test-projects/weather-api`

3. Write permissions to create test outputs in `/mnt/h/Projects/project-prompt/test_results`

4. Optional: An Anthropic API key for testing premium features

## Testing Tools

ProjectPrompt comes with several testing tools:

1. **test_projectprompt.sh**: Basic test script for core features
2. **enhanced_test_projectprompt.sh**: Comprehensive test script for all features
3. **verify_freemium_system.py**: Tool to verify the freemium system implementation
4. **docs/test_report_template.md**: Template for manual testing reports

## Standard Testing Procedure

### Automated Testing

The simplest way to test ProjectPrompt is to run the automated test script:

```bash
cd /mnt/h/Projects/project-prompt
chmod +x enhanced_test_projectprompt.sh
./enhanced_test_projectprompt.sh
```

This will run all test cases and save results in the `/mnt/h/Projects/project-prompt/test_results` directory.

### Manual Testing

For detailed manual testing, follow these steps:

#### 1. Basic Analysis

Test the main analysis feature:

```bash
python /mnt/h/Projects/project-prompt/project_prompt.py analyze /mnt/h/Projects/project-prompt/test-projects/weather-api
```

Verify:
- Script runs without errors
- Basic project statistics are displayed
- Python is identified as the main language
- Correct file counts are shown

#### 2. Project Structure Analysis

Test detailed project structure analysis with JSON output:

```bash
python /mnt/h/Projects/project-prompt/quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api output.json
```

Verify:
- Script runs without errors
- JSON file is created with valid content
- File contains project structure information
- Language statistics match expected values

#### 3. Project Initialization

Test project creation:

```bash
python /mnt/h/Projects/project-prompt/project_prompt.py init test-project --path /tmp
```

Verify:
- Script runs without errors
- Project directory is created
- Standard directories are present (src, tests, docs)
- Basic files are created (README.md, setup.py)

#### 4. Standalone Tools Testing

Test standalone analyzers:

```bash
cd /mnt/h/Projects/project-prompt
python quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api
python project_analyzer.py /mnt/h/Projects/project-prompt/test-projects/weather-api output.json
```

Verify:
- Scripts run without errors
- Output matches the integrated command results
- JSON output is valid (for project_analyzer.py)

#### 5. Advanced Features Testing (When Implemented)

When the documentation generation feature is implemented:

```bash
python /mnt/h/Projects/project-prompt/project_prompt.py docs /mnt/h/Projects/project-prompt/test-projects/weather-api
```

When the connectivity analysis feature is implemented:

```bash
python /mnt/h/Projects/project-prompt/project_prompt.py connections /mnt/h/Projects/project-prompt/test-projects/weather-api
```

#### 6. Freemium System Testing

Test the freemium system implementation:

```bash
cd /mnt/h/Projects/project-prompt
python verify_freemium_system.py
```

With a temporary API key:

```bash
python verify_freemium_system.py --set-key "test-key"
```

## Weather API Test Project

The Weather API test project is designed specifically for testing ProjectPrompt. Its structure includes:

- A primary Python package in `src/`
- A well-structured API client with documentation
- CLI interface for user interaction
- Configuration handling for environment variables
- Test suite in `tests/`
- Documentation in `docs/` and README.md

This structure exercises all the analysis capabilities of ProjectPrompt, including:
- Language detection
- Directory structure analysis
- Dependency mapping
- Documentation extraction
- Code complexity assessment

## Expected Test Results

When testing is successful, you should see:

1. Basic analysis correctly identifies Python as the main language
2. Project structure analysis shows src, tests, docs directories
3. File counts match the actual project (roughly 5-10 Python files)
4. Language breakdown shows predominantly Python files
5. Generated projects have correct basic structure

## Common Issues and Troubleshooting

### Import Errors

If you encounter import errors:

```
ModuleNotFoundError: No module named 'src'
```

Ensure you're running the script from the correct directory or add the project root to your PYTHONPATH.

### File Permission Errors

If you encounter permission errors when creating output files, check the permissions on the target directory:

```bash
chmod -R 755 /mnt/h/Projects/project-prompt/test_results
```

### Missing API Keys for Premium Features

Premium features require API keys. To test premium features:

1. Create a `config.yaml` file with API keys
2. Set environment variables for API keys
3. Use the `--set-key` option with `verify_freemium_system.py`

## Reporting Test Results

For formal testing, use the test report template located at `/mnt/h/Projects/project-prompt/docs/test_report_template.md`.

Fill in the results for each test case and document any issues found along with recommendations.

## Conclusion

This testing guide provides a structured approach to verify ProjectPrompt's functionality. By following these procedures, you can ensure that all features work as expected and identify any issues that need to be addressed.

The provided test scripts automate most of the testing process, but manual verification of results is still recommended for a comprehensive evaluation.
