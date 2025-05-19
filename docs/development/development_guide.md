# Development Guide for Project-Prompt

This guide provides information for developers who want to contribute to the Project-Prompt codebase or understand its internal workings.

## Project Structure

Project-Prompt follows a modular structure organized into the following directories:

```
project-prompt/
├── docs/                    # Documentation files
├── examples/                # Example projects and demos
├── project-output/          # Generated output files
├── scripts/                 # Helper scripts
├── src/                     # Source code
│   ├── analyzers/           # Project analysis modules
│   ├── api/                 # API-related code
│   ├── core/                # Core functionality
│   ├── templates/           # Project templates
│   ├── ui/                  # User interface components
│   └── utils/               # Utility functions
└── tests/                   # Test files
```

For more details, see [DIRECTORY_STRUCTURE.md](../../DIRECTORY_STRUCTURE.md) in the project root.

## Development Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/project-prompt.git
   cd project-prompt
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/macOS
   source venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running Tests

The project uses pytest for unit and integration tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage report
pytest --cov=src
```

## Code Style and Standards

- Follow PEP 8 style guidelines
- Use type hints whenever possible
- Document all public functions and classes with docstrings
- Write unit tests for new functionality

## Building and Packaging

To build a distributable package:

```bash
python -m build
```

## Architecture Overview

Project-Prompt is built with a modular architecture focused on extensibility:

1. **Core Components**:
   - Project scanning and analysis
   - Prompt generation
   - Documentation system

2. **Extension System**:
   - Custom prompt templates
   - Analyzer plugins
   - AI model integrations

## Continuous Integration

The project uses GitHub Actions for CI/CD. The workflows are defined in `.github/workflows/` and include:
- Running tests
- Linting and formatting checks
- Building and publishing packages

## Working with Anthropic API

For details on working with the Anthropic API integration, refer to the [Verification Guide](../guides/verification_guide.md).

## Need Help?

If you need help with development, feel free to:
- Open an issue on GitHub
- Reach out to the maintainers
