# ProjectPrompt User Guide

## Introduction

ProjectPrompt is an intelligent tool that analyzes your code projects and generates contextual prompts for AI assistants. This guide will help you get started with ProjectPrompt and learn how to use all its features effectively.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Analyzing Projects](#analyzing-projects)
4. [Initializing Projects](#initializing-projects)
5. [Generating Prompts](#generating-prompts)
6. [Documentation Generation](#documentation-generation)
7. [Connectivity Analysis](#connectivity-analysis)
8. [Freemium Features](#freemium-features)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for installation from repository)

### From Repository

```bash
# Clone the repository
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Create a command alias
mkdir -p $HOME/bin
ln -sf $(pwd)/project_prompt.py $HOME/bin/project-prompt
chmod +x $HOME/bin/project-prompt

# Add to PATH (if needed)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or source ~/.zshrc
```

### Via Package Manager (Coming Soon)

```bash
# Using pip
pip install project-prompt

# Using Poetry
poetry add project-prompt
```

### Verifying Installation

To verify that ProjectPrompt is correctly installed:

```bash
project-prompt --version
```

You should see output showing the current version.

## Basic Usage

ProjectPrompt provides a command-line interface with several commands:

```bash
project-prompt COMMAND [OPTIONS]
```

Available commands:

- `analyze` - Analyze project structure and functionalities
- `init` - Initialize a new project
- `docs` - Generate project documentation (premium)
- `connections` - Analyze project connectivity (premium)
- `generate-prompts` - Generate contextual prompts
- `set-api` - Configure API keys for premium features
- `config` - Manage configuration
- `menu` - Start interactive menu

Get help for any command using `--help`:

```bash
project-prompt analyze --help
```

## Analyzing Projects

The `analyze` command examines a project's structure and provides insights about its files, languages, and dependencies.

### Basic Analysis

To analyze the current directory:

```bash
project-prompt analyze
```

To analyze a specific project:

```bash
project-prompt analyze /path/to/project
```

### Saving Analysis Results

Save the analysis to a JSON file:

```bash
project-prompt analyze --output analysis.json
```

### Analysis Options

```bash
project-prompt analyze [PATH] [OPTIONS]
```

Options:
- `--output, -o TEXT` - Path to save analysis results
- `--max-files, -m INT` - Maximum files to analyze
- `--max-size, -s FLOAT` - File size limit in MB
- `--functionalities/--no-functionalities` - Enable/disable functionality detection
- `--structure/--no-structure` - Show/hide project structure

### Using the Standalone Analyzer

For faster analysis without dependencies:

```bash
python quick_analyze.py /path/to/project [output.json]
```

For more detailed analysis:

```bash
python project_analyzer.py /path/to/project [output.json]
```

### Understanding Analysis Results

The analysis output includes:

- Project statistics (files, directories, size)
- Language distribution with file counts and line counts
- Important files by category (configuration, documentation, etc.)
- Detected functionalities (when enabled)
- Directory structure (when enabled)

## Initializing Projects

The `init` command creates new projects with a standardized structure.

### Creating a New Project

```bash
project-prompt init my-project
```

This creates a new directory called `my-project` with a standard structure.

### Specifying Project Location

```bash
project-prompt init my-project --path /desired/location
```

### Project Structure

The created project includes:

- `src/` - Source code directory
- `tests/` - Test directory
- `docs/` - Documentation directory
- `README.md` - Project readme
- `setup.py` - Python package configuration
- `.gitignore` - Git ignore file
- Basic module structure in `src/`

## Generating Prompts

The `generate-prompts` command creates contextual prompts for AI assistants based on your project.

### Basic Prompt Generation

```bash
project-prompt generate-prompts
```

### Project-Specific Prompts

```bash
project-prompt generate-prompts /path/to/project
```

### Enhanced Prompts

```bash
project-prompt generate-prompts --enhanced
```

The enhanced option provides more detailed context and better prompts.

### Premium Prompts

```bash
project-prompt generate-prompts --premium
```

Requires a valid API key. Provides the most advanced prompts.

### Saving Prompts

```bash
project-prompt generate-prompts --output prompts.json
```

## Documentation Generation

The `docs` command generates project documentation based on code analysis (premium feature).

### Basic Documentation

```bash
project-prompt docs
```

### Custom Output

```bash
project-prompt docs --output documentation.md
```

### Format Options

```bash
project-prompt docs --format html
```

Supported formats:
- `md` - Markdown (default)
- `html` - HTML
- `json` - JSON

## Connectivity Analysis

The `connections` command analyzes relationships between project components (premium feature).

### Basic Usage

```bash
project-prompt connections
```

### Output Options

```bash
project-prompt connections --output connections.json
```

### Format Options

```bash
project-prompt connections --format dot
```

Supported formats:
- `json` - JSON (default)
- `dot` - GraphViz DOT format
- `graphml` - GraphML format

## Freemium Features

ProjectPrompt uses a freemium model. Basic features are available for free, while advanced features require an API key.

### Free Features

- Basic project analysis
- Project initialization
- Simple prompt generation
- Project structure visualization

### Premium Features

- Enhanced prompt generation
- Documentation generation
- Connectivity analysis
- Implementation suggestions
- Architecture recommendations

### Setting API Keys

```bash
project-prompt set-api anthropic YOUR_API_KEY
```

```bash
project-prompt set-api github YOUR_API_KEY
```

## Configuration

The `config` command manages ProjectPrompt configuration.

### Viewing Configuration

```bash
project-prompt config --list
```

### Setting Configuration Values

```bash
project-prompt config key value
```

Common configuration keys:
- `log_level` - Logging verbosity (info, debug, warning)
- `max_files` - Default maximum files to analyze
- `max_file_size` - Default maximum file size

### Configuration File

The configuration is stored in `config.yaml` in the project directory.

## Troubleshooting

### Common Issues

#### Import Errors

If you encounter import errors, ensure you're running from the correct directory or modify your Python path.

#### File Size Limits

If analysis is skipping large files, increase the size limit:

```bash
project-prompt analyze --max-size 10.0
```

#### API Key Issues

If premium features aren't working, verify your API key:

```bash
project-prompt set-api anthropic YOUR_API_KEY
```

#### Performance Issues

For large projects, limit the number of files:

```bash
project-prompt analyze --max-files 5000
```

### Getting Help

If you encounter persistent issues:

1. Check the documentation in the `docs/` directory
2. Run commands with `--help` for specific options
3. Check for error logs in the terminal output
4. Visit the GitHub repository for more support
