# ProjectPrompt

![CI Status](https://github.com/Dixter999/project-prompt/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1.9-green)](https://github.com/Dixter999/project-prompt/releases)

An intelligent CLI tool that uses AI to analyze code projects, generate documentation, and provide improvement suggestions.

## Features

- **Smart Project Analysis**: Detects technologies, frameworks, and project structure
- **AI-Powered Insights**: Leverages Anthropic Claude and OpenAI for intelligent analysis
- **Visual Dashboard**: Generate comprehensive project dashboards in HTML or Markdown
- **Dependency Analysis**: Advanced dependency mapping with functional groups
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, and more
- **Offline Capable**: Core features work offline, AI features require API keys

## Installation

```bash
pip install projectprompt
```

**Verify installation:**
```bash
project-prompt version
```

### Troubleshooting

If you get `command not found` errors:

**Quick fix:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Alternative method:**
```bash
python -m src.main version
```

**Create `pp` shorthand alias:**
```bash
echo 'alias pp="project-prompt"' >> ~/.zshrc
source ~/.zshrc
# Now use: pp analyze, pp dashboard, etc.
```

📚 **Complete troubleshooting guide:** [INSTALLATION_TROUBLESHOOTING.md](INSTALLATION_TROUBLESHOOTING.md)

## Quick Start

### First Time Setup

1. **Install and verify:**
   ```bash
   pip install projectprompt
   project-prompt version
   ```

2. **Navigate to your project:**
   ```bash
   cd /path/to/your/project
   ```

3. **Start with basic analysis:**
   ```bash
   project-prompt analyze
   project-prompt deps
   project-prompt dashboard
   ```

### Optional: AI-Powered Features

For enhanced analysis with AI insights:

```bash
# Configure API (one-time setup)
project-prompt set-api anthropic
project-prompt verify-api

# Then use premium features
project-prompt premium dashboard
```

### Quick Alias Setup

Create a shorter `pp` command:

```bash
echo 'alias pp="project-prompt"' >> ~/.zshrc
source ~/.zshrc

# Now you can use:
pp analyze
pp dashboard
```

## Commands

### Typical Workflow

For new users, follow this command sequence:

```bash
# 1. First analysis (start here)
project-prompt analyze

# 2. Dependency analysis  
project-prompt deps

# 3. Generate dashboard
project-prompt dashboard

# 4. Optional: Setup AI features
project-prompt set-api anthropic
project-prompt verify-api
project-prompt premium dashboard
```

### Core Commands

| Command | Description |
|---------|-------------|
| `project-prompt analyze` | Analyze project structure and dependencies |
| `project-prompt dashboard` | Generate visual project dashboard |
| `project-prompt deps` | Advanced dependency analysis with functional groups |
| `project-prompt version` | Show version information |
| `project-prompt config` | View configuration |
| `project-prompt set-api <provider>` | Configure API keys (anthropic, github) |
| `project-prompt verify-api` | Test API configuration |

### Dashboard Options

```bash
# Generate markdown dashboard (default)
project-prompt dashboard

# Generate HTML dashboard
project-prompt dashboard --format html

# Premium features (requires API)
project-prompt premium dashboard
```

### Dependency Analysis

```bash
# Basic dependency analysis
project-prompt deps

# Custom output and limits
project-prompt deps --output analysis.md --max-files 500

# Different formats
project-prompt deps --format json
project-prompt deps --format html
```

## Features

### Dependency Analysis

- **Functional Groups**: Automatically groups files by functionality (core, tests, config, etc.)
- **Smart Filtering**: Respects `.gitignore` files and focuses on important files
- **Multiple Formats**: Supports Markdown, JSON, and HTML output
- **Circular Dependencies**: Detects and reports dependency loops
- **Performance**: Uses optimized analysis tools for faster processing

### Dashboard Generation

- **Multiple Formats**: Generate HTML or Markdown dashboards
- **Project Overview**: Comprehensive project structure and metrics
- **AI Insights**: Enhanced analysis with premium features

### Project Analysis

- **Multi-Language**: Supports all major programming languages
- **Technology Detection**: Automatically identifies frameworks and tools
- **Progress Indicators**: Real-time feedback during analysis

## Examples

### Analyze a React Project

```bash
cd my-react-app
project-prompt analyze
project-prompt deps --format html
project-prompt dashboard
```

### Generate Documentation

```bash
# Basic dependency analysis
project-prompt deps --output docs/dependencies.md

# Comprehensive dashboard
project-prompt dashboard --format html

# With AI insights (requires API key)
project-prompt set-api anthropic
project-prompt premium dashboard
```

### Large Project Analysis

```bash
# Focused analysis
project-prompt deps --max-files 1000 --min-deps 5

# Custom output location
project-prompt deps --output /docs/analysis.json --format json
```

## Advanced Features

### .gitignore Support

ProjectPrompt automatically respects your project's `.gitignore` file:

- **Automatic Detection**: Finds and parses `.gitignore` patterns
- **Performance**: Reduces analysis time by skipping irrelevant files
- **Clean Results**: Excludes ignored files for better dependency analysis

### Functional Groups

Files are automatically organized into functional groups:

- **📁 Core Source**: Main application logic and source files
- **🧪 Tests**: Unit tests, integration tests, and test utilities  
- **📚 Documentation**: README files, docs, and guides
- **⚙️ Configuration**: Config files, build scripts, and settings
- **🎨 Assets**: Images, stylesheets, and static resources
- **🔧 Tools**: Build tools, deployment scripts, and utilities

### Output Formats

- **Markdown**: Default format, great for documentation and GitHub
- **HTML**: Rich visual output with styling and interactivity
- **JSON**: Structured data for integration with other tools

## Troubleshooting

### Common Issues

**Command not found:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**API Configuration:**
```bash
project-prompt set-api anthropic
project-prompt verify-api
```

**License/Telemetry Warnings:**
These are harmless and don't affect functionality. ProjectPrompt works offline with basic features.

## Requirements

- Python 3.8+
- Internet connection (for AI features only)
- API keys (optional, for AI-powered analysis)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Dixter999/project-prompt/issues)
- **Documentation**: See [docs/](docs/) directory
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
