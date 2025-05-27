# ProjectPrompt

![CI Status](https://github.com/Dixter999/project-prompt/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/Dixter999/project-prompt/releases)

An intelligent CLI tool that uses AI to analyze code projects, generate documentation, and provide improvement suggestions.

## Features

- **Smart Project Analysis**: Automatically detects technologies, frameworks, and project structure
- **AI-Powered Insights**: Leverages Anthropic Claude and OpenAI for intelligent analysis
- **Interactive CLI**: Beautiful command-line interface with rich output and interactive menus
- **Documentation Tools**: Generate and navigate project documentation
- **Visual Dashboard**: Generate comprehensive project status dashboards
- **Multi-Language Support**: Works with Python, JavaScript, TypeScript, and more
- **Secure Configuration**: Safe API key storage and configuration management
- **Premium Features**: Advanced AI capabilities with subscription management

## Installation

Install ProjectPrompt using pip:

```bash
pip install projectprompt
```

### Verify Installation
```bash
project-prompt version
```

## Getting Started

1. **Install the package**:
   ```bash
   pip install projectprompt
   ```

2. **Navigate to your project directory**:
   ```bash
   cd /path/to/your/project
   ```

3. **Run your first analysis**:
   ```bash
   project-prompt analyze
   ```

4. **Explore with the interactive menu**:
   ```bash
   project-prompt menu
   ```

That's it! ProjectPrompt will analyze your project structure, detect technologies, and provide insights.

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
project-prompt set-api anthropic --key YOUR_API_KEY

# Set OpenAI API key  
project-prompt set-api openai --key YOUR_API_KEY

# Verify API configuration
project-prompt verify-api
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
| `project-prompt verify-api` | Verify API configuration status |
| `project-prompt menu` | Launch interactive menu |
| `project-prompt dashboard` | Generate visual project dashboard |
| `project-prompt docs` | Navigate project documentation |
| `project-prompt help` | Show detailed help information |

### Additional Commands

| Command | Description |
|---------|-------------|
| `project-prompt ai` | Access premium AI features |
| `project-prompt premium` | Manage premium features |
| `project-prompt subscription` | Manage subscription settings |
| `project-prompt telemetry` | Configure anonymous telemetry |
| `project-prompt update` | Check for updates and sync |
| `project-prompt set-log-level` | Change logging verbosity |

## Usage Examples

### Analyze a Project

```bash
# Analyze current directory
project-prompt analyze

# Analyze specific project with custom limits
project-prompt analyze /path/to/project --max-files 1000 --max-size 10.0

# Save analysis to file
project-prompt analyze --output analysis.json

# Generate project dashboard
project-prompt dashboard
```

### Configuration and Setup

```bash
# Interactive setup
project-prompt init

# View configuration
project-prompt config

# Set API keys with prompts
project-prompt set-api anthropic
project-prompt set-api openai

# Verify API status
project-prompt verify-api
```

### Interactive Features

```bash
# Launch interactive menu
project-prompt menu

# Access documentation browser
project-prompt docs

# View detailed help
project-prompt help
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
