# Contributing to ProjectPrompt

Thank you for your interest in contributing to ProjectPrompt! This document provides guidelines and information for contributors.

## Project Structure

ProjectPrompt has the following key components:

- **Main Scripts:**
  - `project_prompt.py` - Main entry point
  - `quick_analyze.py` - Simplified project analyzer
  - `quick_init.py` - Project initialization
  - `project_analyzer.py` - Detailed project analyzer

- **Source Modules:**
  - `src/` - Core functionality components
  - `src/analyzers/` - Project analysis modules
  - `src/generators/` - Documentation and prompt generators
  - `src/utils/` - Utility functions and helpers

- **Documentation:**
  - `docs/` - User and developer documentation
  - `README.md` - Project overview

- **Testing:**
  - `tests/` - Unit tests
  - `test-projects/` - Sample projects for testing
  - `test_projectprompt.sh` - Basic test script
  - `enhanced_test_projectprompt.sh` - Comprehensive test script

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Code Style

Please follow these style guidelines:

- Use PEP 8 for Python code
- Add docstrings to functions and classes
- Keep functions small and focused
- Write clear commit messages

## Testing

Run tests before submitting changes:

```bash
# Run the basic test script
./test_projectprompt.sh

# For comprehensive testing
./enhanced_test_projectprompt.sh
```

## Files to Ignore

The following files are not part of the core project and should not be committed:

- `commit_*.sh` - Git commit scripts
- `*.bak`, `*.original` - Backup files
- `__pycache__/`, `*.pyc` - Python cache files
- `config.yaml` - Local configuration (use `config.yaml.example` instead)

## Creating Clean Pull Requests

Before submitting a pull request, clean up unnecessary files:

```bash
# Run the cleanup script (dry run)
./cleanup_project.sh

# To actually delete unnecessary files
./cleanup_project.sh --execute
```
