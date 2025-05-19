# Anthropic Verification System Documentation

This document provides comprehensive information about the verification system for Anthropic's markdown generation capabilities in ProjectPrompt.

## Overview

The Anthropic verification system is designed to ensure that the markdown generation capabilities of Anthropic's Claude API are functioning correctly within ProjectPrompt. It provides automated testing and quality analysis to validate both functionality and output quality.

## System Components

### 1. Test Project Generation

The system uses the `create_test_project.py` script to generate test projects of various types:

- Web projects (HTML, CSS, JavaScript)
- Backend API projects (FastAPI, models, routes)
- Mobile app projects (React Native)
- Data science projects
- CLI tool projects
- Library projects
- Game development projects
- Mixed projects combining multiple components

Each project type has a carefully designed template structure to represent realistic code projects that Claude would analyze in production.

### 2. Verification Scripts

Several verification scripts are provided to test different aspects of the system:

- **check_anthropic_env.py**: Validates that the environment is properly configured with API keys and required files.
- **quick_test_anthropic.py**: Provides a quick sanity check of the API functionality.
- **enhanced_verify_anthropic.py**: Performs comprehensive verification with detailed quality metrics.
- **advanced_markdown_metrics.py**: Analyzes markdown quality with sophisticated metrics.
- **test_verification_system.py**: Unit tests for the verification components.

### 3. Quality Metrics

The system evaluates the quality of generated markdown using multiple dimensions:

- **Structure**: Presence of headings, hierarchical organization, expected sections
- **Content Richness**: Code blocks, lists, tables, links, and other formatting elements
- **Technical Content**: Code quality terms, technical term density, code analysis
- **Coherence**: Paragraph and sentence structure, flow
- **Anthropic Markers**: Presence of expected Anthropic generation markers

## Usage Guide

### Basic Verification

For basic verification, run the quick test script:

```bash
python quick_test_anthropic.py
```

### Comprehensive Testing

For thorough verification across multiple project types:

```bash
./run_comprehensive_tests.sh
```

To test specific project types:

```bash
python enhanced_verify_anthropic.py --project-types web-project backend-api game-dev
```

### Advanced Markdown Analysis

To perform detailed analysis on a markdown file:

```bash
python advanced_markdown_metrics.py path/to/markdown_file.md --output metrics.json
```

## API Key Configuration

The verification system requires an Anthropic API key, which can be configured in two ways:

1. Set an environment variable:
   ```bash
   export anthropic_API=your_api_key_here
   ```

2. Create a `.env` file in the project root or test-projects directory with:
   ```
   anthropic_API=your_api_key_here
   ```

## Output Files

The verification system generates several types of output files:

- **Markdown files**: Generated analysis from Anthropic API
- **JSON results**: Quality metrics and test results
- **Log files**: Detailed logs from test execution

## Extending the System

### Adding New Project Templates

To add a new project template:

1. Create a directory under `templates/` (e.g., `templates/new-template`)
2. Add required files and directory structure
3. Update the `PROJECT_TYPES` list in `create_test_project.py`
4. Implement any specific customization in the `customize_project` function

### Adding New Quality Metrics

To add new quality metrics:

1. Modify the `advanced_markdown_metrics.py` file
2. Add your metric calculation in the appropriate section
3. Update the scoring system to incorporate your new metric
4. Update the summary output to display the new metric

## Troubleshooting

### Common Issues

- **API Key Not Found**: Ensure the `anthropic_API` key is properly set
- **Template Not Found**: Verify that the requested template exists in the templates directory
- **Failed API Calls**: Check network connectivity and API rate limits
- **Low Quality Scores**: Review the specific metrics to identify which aspects need improvement

## Best Practices

- Always run `check_anthropic_env.py` before starting verification to ensure proper setup
- Use `test_with_anthropic_api.sh` to validate API functionality before running comprehensive tests
- Review quality metrics in detail to understand specific areas that may need attention
- Keep test projects small but representative to avoid API token usage issues
- Store test results for comparison over time to track quality improvements
