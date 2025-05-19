# ProjectPrompt: Intelligent Assistant for Project Analysis and Documentation

Advanced tool that uses AI to analyze projects, generate documentation, and provide improvement suggestions.

## Features

- Analysis of project structure and architecture
- Automatic detection of technologies and frameworks
- Detailed documentation generation
- AI-powered improvement suggestions (Anthropic Claude)
- Integration with existing IDEs and workflows
- Support for multiple programming languages and frameworks

## Prerequisites

* Python 3.8 or higher
* Git (for cloning the repository)
* pip (Python package manager)
* Internet access (for installing dependencies)

## Installation

### Automated Installation (Recommended)

#### For Linux/macOS
```bash
# Clone the repository
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt

# Run the setup script
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

#### For Windows
```powershell
# Clone the repository
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt

# Run the setup script
.\scripts\setup_environment.bat
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Dixter999/project-prompt.git
   cd project-prompt
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

To analyze a project:

```bash
# Basic analysis
python -m src.main analyze /path/to/your/project

# AI-powered analysis (requires Anthropic API key)
python -m src.main analyze /path/to/your/project --ai
```

Results will be saved in the `project-output/analyses` directory.

## Command Line Interface

ProjectPrompt can be used with two command formats:

```bash
# Full command
project-prompt analyze --project /path/to/your/project

# Short alias
pp analyze --project /path/to/your/project
```

Common commands:

```bash
# Analyze a project with advanced model
pp analyze --project /path/to/your/project --model advanced

# Generate documentation
pp generate-docs --project /path/to/your/project --output docs/

# Get help
pp --help
```

## Project Structure

```
project-prompt/
├── docs/                    # Documentation
│   ├── guides/              # User and developer guides
│   ├── reference/           # API reference
│   └── development/         # Development documentation
├── examples/                # Examples and sample projects
│   └── test-projects/       # Test project templates
├── project-output/          # Directory for generated files
│   ├── analyses/            # Project analyses
│   └── suggestions/         # Improvement suggestions
├── scripts/                 # Utility scripts
├── src/                     # Main source code
│   ├── analyzers/           # Code analysis modules
│   ├── api/                 # API integrations
│   ├── core/                # Core functionality
│   ├── generators/          # Content generation modules
│   ├── integrations/        # External service integrations
│   ├── templates/           # Project templates
│   ├── ui/                  # User interface components
│   └── utils/               # Utilities and helper tools
└── tests/                   # Tests
    ├── anthropic/           # Anthropic integration tests
    ├── integration/         # Integration tests
    ├── unit/                # Unit tests
    └── verification/        # Verification tests
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [User Guide](docs/guides/user_guide.md) - Getting started with ProjectPrompt
- [API Reference](docs/reference/api_reference.md) - API documentation
- [Testing Guide](docs/guides/testing_guide.md) - How to test the system
- [Deployment Guide](docs/guides/deployment_guide.md) - Deployment checklist and procedures
- [Development Guide](docs/development/development_guide.md) - For contributors

## Anthropic API Configuration

To use advanced AI features, you need to configure an Anthropic API key:

1. Get an API key from [Anthropic](https://www.anthropic.com/)
2. Configure the API key:
   ```bash
   # Option 1: Environment variable
   export anthropic_API=your_api_key_here
   
   # Option 2: .env file in the project root
   echo "anthropic_API=your_api_key_here" > .env
   ```

3. Available models:
   - Default: Claude 3 Haiku (faster, more economical)
   - Advanced: Claude 3.7 Sonnet (more detailed analysis)

   You can specify which model to use:
   ```bash
   pp analyze --project /path/to/your/project --model advanced
   ```

## Configuration Options

You can customize ProjectPrompt behavior in your `.env` file:

```bash
# Claude API settings
anthropic_API=your_api_key_here
ANTHROPIC_VERSION=2023-06-01

# Model settings
DEFAULT_MODEL=claude-3-haiku-20240307
ADVANCED_MODEL=claude-3-7-sonnet-20240620

# Generation parameters
MAX_TOKENS=4000
TEMPERATURE=0.7

# Other settings
TELEMETRY_ENABLED=true
LOG_LEVEL=info
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the project.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
