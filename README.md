# ProjectPrompt

![CI Status](https://github.com/Dixter999/project-prompt/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/Dixter999/project-prompt/releases)

An intelligent CLI tool that uses AI to analyze code projects, generate documentation, and provide improvement suggestions.

## Features

- **Smart Project Analysis**: Automatically detects technologies, frameworks, and project structure
- **AI-Powered Insights**: Leverages Anthropic Claude and OpenAI for intelligent analysis
- **Interactive CLI**: Beautiful command-line interface with rich output
- **Documentation Tools**: Generate and navigate project documentation
- **Multi-Language Support**: Works with Python, JavaScript, TypeScript, and more

## Installation

```bash
pip install projectprompt
```

### Verify Installation
```bash
project-prompt version
```

## Quick Start

### Basic Commands

```bash
# Show version and help
project-prompt version
project-prompt --help

# Analyze your current project
project-prompt analyze

# Analyze a specific project
project-prompt analyze /path/to/project

# Interactive menu
project-prompt menu
```

## Configuration

### Set Up AI API Keys (Optional)

To use advanced AI features, configure your API keys:

```bash
# Set Anthropic API key
project-prompt set-api anthropic YOUR_API_KEY

# Set OpenAI API key  
project-prompt set-api openai YOUR_API_KEY

# Verify API configuration
project-prompt config
```

### Configuration Commands

```bash
# View current configuration
project-prompt config

# Initialize configuration with interactive setup
project-prompt init

# Access configuration menu
project-prompt menu
```

## Core Commands

| Command | Description |
|---------|-------------|
| `project-prompt version` | Show version information |
| `project-prompt analyze` | Analyze project structure and detect technologies |
| `project-prompt init` | Initialize new project or configuration |
| `project-prompt config` | View and manage configuration |
| `project-prompt set-api` | Configure API keys for AI features |
| `project-prompt menu` | Launch interactive menu |

## Usage Examples

### Analyze a Project

```bash
# Analyze current directory
project-prompt analyze

# Analyze specific project with custom limits
project-prompt analyze /path/to/project --max-files 1000 --max-size 10.0

# Save analysis to file
project-prompt analyze --output analysis.json
```

### Get Help

```bash
# General help
project-prompt --help

# Command-specific help
project-prompt analyze --help
project-prompt config --help
```

## Requirements

- Python 3.8+ (tested on 3.8, 3.9, 3.10, 3.11)
- Internet connection (for AI features)
- API keys for Anthropic Claude or OpenAI (optional, for advanced features)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/Dixter999/project-prompt/issues)
- **Documentation**: Full documentation available in the [docs](docs/) directory
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for release history
