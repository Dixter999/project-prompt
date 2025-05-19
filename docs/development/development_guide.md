# ProjectPrompt Development Guide

This comprehensive guide provides developers with the information needed to work on or contribute to the ProjectPrompt project.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Development Environment Setup](#development-environment-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style and Standards](#code-style-and-standards)
- [Contribution Guidelines](#contribution-guidelines)
- [Release Process](#release-process)

## Project Overview

ProjectPrompt is an intelligent assistant for analyzing code projects, generating documentation, and providing improvement suggestions. The system uses AI (primarily Anthropic's Claude models) to generate contextually relevant analysis and recommendations.

### Core Functionality

- **Project Analysis**: Scans and understands project structure and code patterns
- **Documentation Generation**: Creates detailed documentation from code analysis
- **AI Integration**: Uses Claude models to enhance analysis and generate insights
- **Improvement Suggestions**: Provides actionable recommendations for code quality

## Architecture

ProjectPrompt follows a modular architecture with clear separation of concerns:

```
project-prompt/
├── docs/                    # Documentation files
│   ├── guides/              # User and developer guides
│   ├── reference/           # API reference
│   └── development/         # Development documentation
├── examples/                # Example projects and demos
│   ├── projects/            # Sample projects
│   └── test-projects/       # Test project templates
├── project-output/          # Generated output files
│   ├── analyses/            # Project analysis reports
│   └── suggestions/         # Improvement suggestions
├── scripts/                 # Shell scripts and utilities
├── src/                     # Source code
│   ├── analyzers/           # Project analysis modules
│   ├── api/                 # API-related code
│   ├── core/                # Core functionality
│   ├── generators/          # Content generation modules
│   ├── integrations/        # External service integrations
│   ├── templates/           # Project templates
│   ├── ui/                  # User interface components
│   └── utils/               # Utility functions
└── tests/                   # Test files
    ├── anthropic/           # Anthropic-specific tests
    ├── e2e/                 # End-to-end tests
    ├── integration/         # Integration tests
    ├── unit/                # Unit tests
    └── verification/        # Verification tests
```

## Key Components

### Core Functionality (`src/core/`)

The central project logic that orchestrates all operations:

- `project_prompt.py`: Main business logic and orchestration
- `analyze_with_anthropic_direct.py`: Direct Anthropic AI integration
- `project_analyzer.py`: Project structure and dependency analysis

### Project Analysis (`src/analyzers/`)

Modules for analyzing various aspects of a project:

- `file_analyzer.py`: Analyzes individual files and their contents
- `dependency_analyzer.py`: Detects project dependencies
- `structure_analyzer.py`: Analyzes project structure and organization
- `framework_detector.py`: Identifies frameworks and libraries in use

### Generators (`src/generators/`)

Content generation components:

- `documentation_generator.py`: Generates documentation from analysis
- `suggestion_generator.py`: Creates improvement suggestions
- `prompt_generator.py`: Creates contextual prompts for AI models

### AI Integrations (`src/integrations/`)

Integration with AI services:

- `anthropic_integrator.py`: Integration with Anthropic's Claude models
- `model_selector.py`: Logic for choosing appropriate AI models
- `response_processor.py`: Processes and formats AI responses

### User Interfaces (`src/ui/`)

User interface components:

- `cli.py`: Command-line interface implementation
- `interactive_menu.py`: Interactive menu system
- `report_formatter.py`: Formats output for display

### Utilities (`src/utils/`)

Helper functions and tools:

- `config_manager.py`: Configuration handling
- `file_utils.py`: File system operations
- `logger.py`: Logging functionality
- `telemetry.py`: Usage data collection (optional)

## Development Environment Setup

### Prerequisites

- Python 3.8 or later
- Git
- A text editor or IDE (VS Code recommended)
- Anthropic API key (for AI-related features)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/projectprompt/project-prompt.git
   cd project-prompt
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Anthropic API key and other settings
   ```

5. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

## Development Workflow

### Feature Development Process

1. **Create a feature branch** from the main development branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement your changes** following the code style guidelines

3. **Write tests** for your new functionality

4. **Run tests locally** to verify your changes:
   ```bash
   pytest tests/unit
   pytest tests/integration
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request** through GitHub

### Working with AI Components

When developing AI-related features:

1. Use the test API key for development
2. Set `LOG_RESPONSES=true` in your `.env` file to log AI responses
3. Use the development models (`DEFAULT_MODEL` in `.env`) to save costs
4. For final testing, validate with the production model

## Testing

ProjectPrompt uses a comprehensive testing strategy:

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run tests with coverage report
pytest --cov=src

# Run Anthropic-specific tests
bash tests/run_anthropic_verification.sh
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test interactions between components
- **E2E Tests**: Test the entire system workflow
- **Anthropic Tests**: Test AI integration specifically
- **Verification Tests**: Validate output quality

### Writing Tests

- Place tests in the appropriate directory based on type
- Name test files with `test_` prefix
- Use fixtures for common setup operations
- Mock external APIs for unit and integration tests

## Code Style and Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use type hints for function arguments and return values
- Write docstrings for all public methods and functions

### Documentation Standards

- Use Google-style docstrings
- Include examples in docstrings where appropriate
- Keep documentation updated with code changes
- Document complex algorithms with comments

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- Types: feat, fix, docs, style, refactor, test, chore
- Example: `feat(analyzer): Add JavaScript framework detection`

## Contribution Guidelines

### What We're Looking For

- Bug fixes
- Performance improvements
- New analyzers for different languages/frameworks
- Enhanced AI integration
- Documentation improvements

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Make your changes
5. Ensure tests pass
6. Submit a pull request with a clear description

### Code Review Process

- All PRs require at least one review
- Address all review comments
- Maintain test coverage above 80%
- CI checks must pass

## Release Process

### Version Numbering

ProjectPrompt follows semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Incompatible API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Steps

1. Update version number in `setup.py`, `__init__.py`, and documentation
2. Update CHANGELOG.md with all notable changes
3. Create and merge a release PR
4. Tag the release with the version number
5. Build and publish package to PyPI
6. Create GitHub release with release notes

For more detailed information about the project architecture, see the [Architecture](architecture.md) document.
