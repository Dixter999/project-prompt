# Testing Anthropic Markdown Generation

This directory contains tools and scripts for testing and verifying the markdown generation capabilities of Anthropic's Claude API in ProjectPrompt.

## Overview

ProjectPrompt uses Anthropic's Claude API to analyze projects and generate insightful markdown reports with recommendations. This testing suite helps verify that the integration is working correctly and producing high-quality markdown output.

## Test Files

| File | Description |
|------|-------------|
| `quick_test_anthropic.py` | Simple test that creates a small project and runs Anthropic analysis |
| `run_all_verifications.sh` | Comprehensive script that runs all verification methods |
| `README.md` | This file, explaining the testing process |

## Setting Up

1. **API Key Configuration**

   Before running tests, you need to set up an Anthropic API key:

   ```bash
   # Create .env file in project root or test-projects directory
   echo "anthropic_API=your_api_key_here" > .env
   
   # Or set environment variable directly
   export anthropic_API=your_api_key_here
   ```

2. **Dependencies**

   Make sure all dependencies are installed:

   ```bash
   cd /mnt/h/Projects/project-prompt
   pip install -r requirements.txt
   ```

## Running Tests

### Quick Test

For a quick verification that the Anthropic generation is working:

```bash
cd /mnt/h/Projects/project-prompt
./test-projects/quick_test_anthropic.py
```

This script:
- Creates a simple test project
- Runs Anthropic analysis on it
- Verifies the output contains proper markdown content

### Complete Verification

For comprehensive testing:

```bash
cd /mnt/h/Projects/project-prompt
./test-projects/run_all_verifications.sh
```

This runs:
1. Quick test
2. Basic verification
3. Comprehensive test suite

You can also specify a project to analyze:

```bash
./test-projects/run_all_verifications.sh --project /path/to/your/project
```

Or skip specific tests:

```bash
./test-projects/run_all_verifications.sh --skip-quick --skip-full
```

## Understanding Test Results

### Success Indicators:

- ✓ Green check marks indicate successful tests
- Output files should contain proper markdown with structured sections
- Anthropic-generated content should be present in the "Sugerencias de Mejora" section

### Common Issues:

- **API Key Invalid**: Check that your Anthropic API key is valid and properly set
- **Empty Output**: Verify that the project has enough content for meaningful analysis
- **Missing Sections**: Ensure that your prompt templates are properly formatted
- **Rate Limiting**: If performing multiple tests, you might hit API rate limits

## Test Outputs

All test outputs are saved in the `test-projects` directory with descriptive filenames:

- `quick_test_output_*.md`: Results from quick tests
- `anthropic_analysis_*.md`: Results from comprehensive tests
- `basic_verification_result.md`: Results from basic verification

## Further Reading

For more detailed information on the Anthropic verification process, refer to:
- `/mnt/h/Projects/project-prompt/docs/anthropic_verification_guide.md`

## Improving the Tests

If you want to improve these tests:

1. **Add More Project Types**: Create additional test project types in `test_anthropic_markdown_generation.py`
2. **Enhance Quality Metrics**: Refine the quality assessment logic in the verification scripts
3. **Add Regression Tests**: Create tests that verify specific known issues don't reoccur
4. **Automate Regular Testing**: Set up a cron job to periodically run verification tests
