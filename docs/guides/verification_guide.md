# Anthropic Markdown Generation Verification Guide

This guide provides a comprehensive overview of the verification process for Anthropic's markdown generation capabilities in ProjectPrompt.

## Overview

ProjectPrompt utilizes Anthropic's Claude API to analyze code projects and generate insightful markdown reports. The verification system ensures:

1. Proper API connectivity
2. High-quality markdown generation 
3. Presence of expected analysis sections
4. Correct handling of different project types
5. Consistent output quality
6. Detailed quality metrics for evaluating content
7. Automated validation across multiple project templates

## Requirements

1. Valid Anthropic API key
2. Internet access to connect to Anthropic API
3. Python 3.8 or higher installed
4. ProjectPrompt installed and configured

## Configuración de la Clave API

Para configurar la clave API de Anthropic, puedes utilizar cualquiera de estos métodos:

1. **Archivo .env**: Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```
   anthropic_API=tu_clave_api_aquí
   ```

2. **Variable de entorno**: Exportar la variable de entorno en tu shell:
   ```bash
   export anthropic_API=tu_clave_api_aquí
   ```

3. **Directamente en los scripts de prueba**: Pasar la clave API como parámetro:
   ```bash
   python verify_anthropic_generation.py --api-key=tu_clave_api_aquí
   ```

## Available Test Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `quick_test_anthropic.py` | Fast test with a simple project | Quick sanity check |
| `verify_anthropic_generation.py` | Basic verification of output format | Verifying markdown structure |
| `enhanced_verify_anthropic.py` | Quality metrics assessment | Deeper validation of content quality |
| `test_anthropic_markdown_generation.py` | Full test suite with multiple project types | Comprehensive testing |
| `create_test_project.py` | Generate test projects of various types | Creating test fixtures |
| `run_comprehensive_tests.sh` | Run all verification methods | Complete verification process |

## Verification Scripts

The project includes several scripts for verifying markdown generation:

### 1. Basic Verification Script

This script verifies that markdown generation works correctly for a specific project:

```bash
python verify_anthropic_generation.py [path/to/project]
```

Options:
- `path/to/project`: Path to the project to analyze (default: current directory)
- `-o, --output`: Output file for the analysis (default: anthropic_analysis_output.md)

### 2. Quick Test Script

For a fast verification of API functionality:

```bash
python test-projects/quick_test_anthropic.py
```

### 3. Enhanced Verification Script

For detailed quality assessment with multiple project types:

```bash
python test-projects/enhanced_verify_anthropic.py --project-types web-project backend-api
```

### 4. Advanced Markdown Metrics Analysis

For in-depth quality assessment of generated markdown:

```bash
python test-projects/advanced_markdown_metrics.py path/to/markdown_file.md
```

Options:
- `--output`: Save metrics to JSON file
- `--html`: Generate HTML report of analysis

### 5. Unit Testing Suite

Run the unit tests to verify the verification system itself:

```bash
python test-projects/test_verification_system.py
```

### 6. API Testing Script

Test with actual API calls:

```bash
./test-projects/test_with_anthropic_api.sh
```

### 7. Comprehensive Test Script

The most thorough testing across all supported project types:

```bash
python test_anthropic_markdown_generation.py [--api-key your_api_key]
```

Options:
- `--api-key`: Anthropic API key (optional if configured through other means)
- `--skip-project-creation`: Skip test project creation and use an existing project
- `--project-path`: Path to an existing project (use with --skip-project-creation)

## Running Comprehensive Tests

For the most thorough verification across all supported project types:

```bash
cd /mnt/h/Projects/project-prompt
./test-projects/run_comprehensive_tests.sh
```

Options:
```
--skip-env-check       Skip environment check
--skip-quick           Skip quick test
--skip-basic           Skip basic verification
--skip-enhanced        Skip enhanced verification
--skip-comprehensive   Skip comprehensive testing
--project PATH         Path to existing project to analyze
--types TYPE1 TYPE2    Project types to test
```

Available project types:
- `web-project`: Frontend web application
- `backend-api`: Backend API server
- `mobile-app`: Mobile application
- `data-science`: Data analysis/ML project
- `cli-tool`: Command-line tool
- `library`: Reusable library/package
- `mixed`: Multi-component project

## Result Interpretation

### Markdown Analysis Results

The analysis of a project should generate a markdown file with the following sections:

1. **Project Analysis** - General information
2. **General Statistics** - Data about files and size
3. **Language Distribution** - Table with languages used
4. **Important Files** - List of key files

### Anthropic-Generated Sections

The part generated by Anthropic should include:

1. **Summary/Purpose/Structure** - General project description
2. **Strengths** - Identified positive aspects
3. **Weaknesses/Areas for Improvement** - Issues or weak points
4. **Recommendations/Suggestions** - Specific improvement proposals

## Quality Metrics

The verification tools check the following aspects of generated markdown:

1. **Structure completeness**:
   - Proper headings hierarchy
   - All required sections present
   - Balanced content distribution

2. **Content richness**:
   - Number of headings
   - Presence of code examples
   - List items for structured information
   - Word count and text density

3. **Technical accuracy**:
   - Project purpose identification
   - Recognition of programming languages
   - Detection of important files and patterns
   - Relevant recommendations

4. **Output consistency**:
   - Consistent structure across different project types
   - Predictable section organization

## Test Output

All verification tools save their outputs to the `/mnt/h/Projects/project-prompt/test-projects/` directory:

- Markdown files with generated analysis
- JSON files with verification results
- Log files with test summaries

## Troubleshooting

### API Key Issues

**Symptom**: "API key not found" or authentication errors
**Solution**: Ensure your API key is correctly set in the environment or .env file

### Rate Limiting

**Symptom**: API requests fail after multiple tests
**Solution**: Add delays between tests or run fewer project types at once

### Quality Below Threshold

**Symptom**: Quality metrics fail despite successful API response
**Solution**: 
- Check if the project is too simple or lacks sufficient content
- Try a different project type or add more content to test projects
- Adjust quality thresholds in the scripts if needed

### Missing Dependencies

**Symptom**: Import errors when running scripts
**Solution**: Run `pip install -r requirements.txt` to install all needed packages

## Usage Examples

### Basic Example

```bash
# Verify current project
python verify_anthropic_generation.py

# Verify a specific project
python verify_anthropic_generation.py /path/to/my/project

# Save analysis to a specific file
python verify_anthropic_generation.py -o my_project_analysis.md
```

### Advanced Tests

```bash
# Run quick test
python test-projects/quick_test_anthropic.py

# Run enhanced verification with specific project types
python test-projects/enhanced_verify_anthropic.py --project-types web-project backend-api

# Run comprehensive tests
./test-projects/run_comprehensive_tests.sh
```

## Extending the Verification System

To add new project types for testing:

1. Create a new template in `/test-projects/templates/[type-name]/`
2. Add the type to `PROJECT_TYPES` in `create_test_project.py`
3. Create relevant sample files that demonstrate project complexity

## CI/CD Integration

For automated testing, you can add the verification script to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
jobs:
  verify_anthropic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Verify Anthropic integration
        env:
          anthropic_API: ${{ secrets.ANTHROPIC_API_KEY }}
        run: ./test-projects/run_comprehensive_tests.sh --skip-comprehensive
```
