# ProjectPrompt

![CI Status](https://github.com/Dixter999/project-prompt/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/Dixter999/project-prompt/releases)

An intelligent CLI tool that uses AI to analyze code projects, generate documentation, and provide improvement suggestions.

## Features

- **Smart Project Analysis**: Automatically detects technologies, frameworks, and project structure with real-time progress indicators
- **AI-Powered Insights**: Leverages Anthropic Claude and OpenAI for intelligent analysis and recommendations
- **Interactive CLI**: Beautiful command-line interface with rich output, progress bars, and interactive menus
- **Documentation Tools**: Generate and navigate project documentation with multiple output formats
- **Visual Dashboard**: Generate comprehensive project status dashboards in HTML or Markdown format
- **Real-Time Progress**: Live progress indicators during project scanning showing current files and status
- **Multi-Language Support**: Works with Python, JavaScript, TypeScript, Java, C++, and more
- **Secure Configuration**: Safe API key storage and configuration management with .env support
- **Premium Features**: Advanced AI capabilities with subscription management
- **Offline Capable**: Core features work completely offline, premium features only need API keys

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

That's it! ProjectPrompt will analyze your project structure, detect technologies, and provide insights with real-time progress indicators showing exactly what's being processed.

## Progress Indicators

ProjectPrompt includes comprehensive progress indicators during analysis to keep you informed:

- **File Scanning Progress**: Shows current file being analyzed and total progress percentage
- **Directory Navigation**: Displays which directories are being scanned
- **Analysis Phases**: Reports on dependency analysis, language detection, and important file identification
- **Real-Time Updates**: Progress bar updates every 100ms with current status
- **Professional Display**: Uses rich formatting with file counts and visual progress bars

Example progress display:
```
🔍 Analyzing Project... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 65% (1,234/1,890 files)
📁 Current: src/components/UserProfile.tsx
🔄 Status: Analizando archivo
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

ProjectPrompt uses the secure .env file approach for API key configuration:

```bash
# Configure Anthropic API (guides you through .env setup)
project-prompt set-api anthropic

# Configure GitHub API (guides you through .env setup)
project-prompt set-api github

# Check your current .env configuration
project-prompt check-env

# Verify API configuration and functionality
project-prompt verify-api
```

**Secure .env Method (Recommended):**
1. Create a `.env` file in your project root
2. Add your API keys:
   ```
   # Anthropic Claude API
   anthropic_API=your_anthropic_key_here
   
   # GitHub API (optional)
   GITHUB_API_KEY=your_github_key_here
   ```
3. Ensure `.env` is in your `.gitignore`
4. Run `project-prompt verify-api` to test

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
| `project-prompt deps` | Analyze project dependencies with functional groups and .gitignore support |
| `project-prompt init` | Initialize new project or configuration |
| `project-prompt config` | View and manage configuration |
| `project-prompt set-api` | Configure API keys for AI features |
| `project-prompt verify-api` | Verify API configuration status |
| `project-prompt menu` | Launch interactive menu |
| `project-prompt dashboard` | Generate visual project dashboard (HTML or Markdown) |
| `project-prompt docs` | Navigate project documentation |
| `project-prompt help` | Show detailed help information |

### Dashboard Commands

| Command | Description | Example |
|---------|-------------|---------|
| `project-prompt dashboard` | Generate markdown dashboard (default format) | `project-prompt dashboard` |
| `project-prompt dashboard --format html` | Generate HTML dashboard | `project-prompt dashboard --format html` |
| `project-prompt dashboard --format markdown` | Generate markdown dashboard | `project-prompt dashboard --format markdown` |
| `project-prompt premium dashboard` | Generate premium HTML dashboard | `project-prompt premium dashboard` |
| `project-prompt premium dashboard --format html` | Generate premium HTML dashboard | `project-prompt premium dashboard --format html` |
| `project-prompt premium dashboard --format markdown` | Generate premium Markdown dashboard | `project-prompt premium dashboard --format markdown` |
| `project-prompt premium dashboard --format md` | Generate premium Markdown dashboard (short) | `project-prompt premium dashboard --format md` |

### Dependency Analysis Commands

| Command | Description | Example |
|---------|-------------|---------|
| `project-prompt deps` | Analyze dependencies (basic) | `project-prompt deps` |
| `project-prompt deps --output analysis.md` | Generate dependency analysis report | `project-prompt deps --output analysis.md` |
| `project-prompt deps --max-files 200 --min-deps 5` | Custom dependency thresholds | `project-prompt deps --max-files 200 --min-deps 5` |
| `project-prompt deps --format json` | Generate JSON dependency report | `project-prompt deps --format json --output deps.json` |
| `project-prompt deps --no-madge` | Use traditional analysis (slower) | `project-prompt deps --no-madge` |
| `project-prompt deps --no-groups` | Skip functionality grouping | `project-prompt deps --no-groups` |
| `project-prompt deps --no-cycles` | Skip circular dependency detection | `project-prompt deps --no-cycles` |

#### Dependency Analysis Features

- **Functional Groups**: Automatically detects and groups files by functionality (core, tests, configuration, etc.)
- **Textual Dependency Visualization**: Generates clear textual representations of dependency relationships
- **Enhanced Markdown Output**: Comprehensive reports with functional groups, exclusion statistics, and dependency metrics
- **Automatic .gitignore Support**: Respects `.gitignore` files automatically, excluding ignored files from analysis
- **Analysis Caching**: Prevents duplicate analysis during the same session for improved performance
- **Efficient Analysis**: Uses Madge for fast dependency parsing when available
- **Smart Filtering**: Focuses on important files with configurable thresholds
- **Multiple Output Formats**: Supports Markdown (default), JSON, and HTML outputs
- **Circular Dependency Detection**: Identifies problematic dependency loops
- **Enhanced Progress Indicators**: Real-time progress with emoji indicators and descriptive messages

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

### Project Analysis

```bash
# Analyze current directory with progress indicators
project-prompt analyze

# Analyze specific project with custom limits
project-prompt analyze /path/to/project --max-files 1000 --max-size 10.0

# Save analysis to file
project-prompt analyze --output analysis.json

# Quick analysis with minimal output
project-prompt analyze --quiet
```

### Dependency Analysis

```bash
# Generate functional groups analysis in markdown (default format)
project-prompt deps

# Generate comprehensive dependency analysis with functional groups
project-prompt deps --max-files 500 --min-deps 10

# Generate specific format with functional groups
project-prompt deps --format json
project-prompt deps --format html

# Save to custom location with functional groups
project-prompt deps --output dependency_analysis.md
project-prompt deps --output /custom/path/deps.json --format json

# Quick analysis without circular dependency detection
project-prompt deps --no-cycles --max-files 100

# Traditional analysis (no Madge optimization)
project-prompt deps --no-madge

# Focused analysis without functionality grouping
project-prompt deps --no-groups --min-deps 5

# Complete analysis with all features including functional groups
project-prompt deps --max-files 1000 --format html
```

**New Functional Groups Feature**:
- 🏗️ **Automatic Detection**: Groups files by functionality (core source, tests, documentation, configuration)
- 📊 **Textual Visualization**: Clear textual representation of dependency relationships within groups  
- 📋 **Enhanced Reporting**: Shows functional groups instead of just "important files analyzed"
- 🔍 **Smart Analysis**: Based on directory structure, file types, and circular dependencies

**Output Organization**: 
- 📁 Automatic outputs saved to `project-output/analyses/dependencies/`
- 🕒 Timestamped filenames: `deps_project-name_YYYYMMDD_HHMMSS.format`
- 🎯 Use `--output` for custom locations
- 📝 Default format is now **markdown** for better readability

### Dashboard Generation

```bash
# Generate basic markdown dashboard (new default format)
project-prompt dashboard

# Generate basic HTML dashboard
project-prompt dashboard --format html

# Generate premium HTML dashboard with advanced features
project-prompt premium dashboard

# Generate premium Markdown dashboard for GitHub/documentation
project-prompt premium dashboard --format markdown

# Generate premium Markdown dashboard (short format)
project-prompt premium dashboard --format md

# Dashboard will be saved as:
# - HTML: project_dashboard.html
# - Markdown: project_dashboard.md (new default format for better GitHub integration)
```

### Configuration and Setup

```bash
# Interactive setup wizard
project-prompt init

# View current configuration
project-prompt config

# Set API keys with guided prompts
project-prompt set-api anthropic
project-prompt set-api openai
project-prompt set-api github

# Verify API status and connectivity
project-prompt verify-api

# Check .env file configuration
project-prompt check-env
```

### Interactive Features

```bash
# Launch interactive menu with all features
project-prompt menu

# Access documentation browser
project-prompt docs

# View detailed help for any command
project-prompt help
project-prompt analyze --help
project-prompt dashboard --help
```

### Advanced Usage

```bash
# Set custom log levels for debugging
project-prompt set-log-level debug
project-prompt set-log-level info
project-prompt set-log-level warning

# Manage telemetry settings
project-prompt telemetry enable
project-prompt telemetry disable
project-prompt telemetry status

# Check for updates
project-prompt update

# Access AI features (requires API keys)
project-prompt ai

# Manage premium features
project-prompt premium
project-prompt subscription
```

### Real-World Examples

```bash
# Analyze a React project dependencies with functional groups and generate documentation
cd my-react-app
project-prompt deps --output react_dependencies.md
project-prompt premium dashboard --format markdown

# Analyze a Python project with functional groups (respects .gitignore)
cd my-python-project
project-prompt deps --max-files 2000 --min-deps 3
project-prompt premium dashboard

# Setup for a new team member
project-prompt init
project-prompt set-api anthropic
project-prompt menu

# Generate comprehensive project analysis with functional groups
project-prompt analyze
project-prompt deps --output full_analysis.md
project-prompt premium dashboard --format md

# Quick dependency overview with functional groups for code review
project-prompt deps --max-files 50 --output quick_deps.md

# Large project analysis with functional groups and optimizations
project-prompt deps --max-files 1000 --min-deps 8 --format json --output enterprise_deps.json
```

## .gitignore Support

ProjectPrompt automatically respects your project's `.gitignore` file during analysis:

### Features

- **Automatic Detection**: Finds and parses `.gitignore` in your project root
- **Standard Syntax Support**: Supports all standard .gitignore patterns including:
  - Wildcards (`*`, `**`)
  - Directory patterns (`/`, trailing `/`)
  - Negation patterns (`!`)
  - Comments (`#`)
- **Improved Analysis**: Excludes ignored files from dependency analysis for cleaner results
- **Performance**: Reduces analysis time by skipping irrelevant files
- **Transparency**: Reports how many files were excluded by .gitignore rules

### Example .gitignore Integration

```bash
# Your .gitignore might contain:
node_modules/
*.log
dist/
.env
__pycache__/

# ProjectPrompt will automatically exclude these patterns during analysis
project-prompt deps --output clean_analysis.md

# Output will show:
# "Total de archivos excluidos: 1,234"
# "Por .gitignore: 1,156 archivos"
```

## Functional Groups Feature

ProjectPrompt now automatically detects and organizes your project files into functional groups, providing better insights into your project structure:

### What are Functional Groups?

Functional groups are automatically detected collections of files that serve similar purposes in your project:

- **📁 Core Source Code**: Main application logic and source files
- **🧪 Tests**: Unit tests, integration tests, and test utilities  
- **📚 Documentation**: README files, documentation, and guides
- **⚙️ Configuration**: Config files, build scripts, and project settings
- **🎨 Assets**: Images, stylesheets, and static resources
- **🔧 Tools & Scripts**: Build tools, deployment scripts, and utilities

### How It Works

```bash
# Run dependency analysis with functional groups
project-prompt deps

# Example output shows functional groups instead of just file counts:
# ✅ Análisis completado: 45 archivos, 6 grupos funcionales
# 
# 📊 Grupos Funcionales Detectados:
# 1. Core Source Code (src/)
#    - 15 archivos de código principal
#    - Funcionalidad: Lógica principal de la aplicación
# 
# 2. Tests (tests/)
#    - 8 archivos de pruebas
#    - Funcionalidad: Pruebas unitarias y de integración
```

### Benefits

- **🔍 Better Project Understanding**: See how your project is organized functionally
- **📊 Clearer Analysis**: Groups replace generic "important files" counts  
- **🎯 Focused Insights**: Understand dependencies within and between functional areas
- **📈 Improved Reporting**: Enhanced markdown output with group-specific visualizations
- **⚡ Smart Detection**: Based on directory structure, file types, and dependency patterns

### Manual Override

If you need to analyze files normally ignored by git:

```bash
# Use traditional analysis without gitignore (not recommended for most cases)
# Note: Currently this requires custom configuration
project-prompt analyze --max-files 10000  # Basic analysis ignores .gitignore by default
```

## Enhanced Output Formats

ProjectPrompt now provides improved output formats with better structure and readability:

### Markdown Output (New Default)

- **📝 Default Format**: Dependency analysis now defaults to markdown for better GitHub integration
- **🏗️ Functional Groups**: Clear sections showing detected functional groups with descriptions
- **📊 Enhanced Statistics**: Comprehensive metrics including .gitignore exclusions
- **🎯 Textual Visualization**: ASCII-style dependency graphs within functional groups
- **📋 Structured Sections**: Organized layout with metrics, groups, exclusions, and dependencies

### Example Enhanced Output Structure

```markdown
# 📊 Análisis de Dependencias del Proyecto

## 📈 Resumen Ejecutivo
- **Archivos analizados**: 45
- **Grupos funcionales**: 6
- **Archivos excluidos (.gitignore)**: 234

## 🏗️ Grupos Funcionales Detectados

### 1. Core Source Code (src/)
**Tipo:** source
**Archivos:** 15
**Descripción:** Lógica principal de la aplicación

**Grafo del grupo:**
```
[1] main.py → [2] analyzer.py
[2] analyzer.py → [3] utils.py
[3] utils.py → [4] config.py
```

## 📋 Archivos Excluidos por .gitignore
✅ **234 archivos excluidos** por las reglas de .gitignore
```

### Benefits of Enhanced Output

- **🔍 Better Project Understanding**: Clear functional organization
- **📊 Professional Reports**: Suitable for documentation and team sharing  
- **⚡ Quick Insights**: Fast overview of project structure and dependencies
- **🎯 Actionable Information**: Identify important files and potential issues
- **📈 Progress Tracking**: Compare project evolution over time

## Troubleshooting

### Common Issues

#### License Server Connection Error

If you see the following error:
```
WARNING: No se pudo contactar al servidor de licencias: 
         HTTPSConnectionPool(host='api.projectprompt.dev', port=443): Max retries exceeded...
```

**Solution:** This is normal when running offline. ProjectPrompt works completely offline with basic features. Premium features only require API keys, not an online license verification.

#### Telemetry Initialization Error

If you see the following error:
```
ERROR: Error al inicializar telemetría: 'ConfigManager' object has no attribute 'get_config'
```

**Solution:** This is a harmless error and doesn't affect any functionality. Telemetry is optional and ProjectPrompt will continue to work normally without it.

#### API Not Configured

If you see "Not configured ❌" for APIs:

**Solution:**
```bash
# Configure Anthropic API with secure .env method
project-prompt set-api anthropic

# Configure GitHub API with secure .env method
project-prompt set-api github

# Check your .env configuration
project-prompt check-env

# Verify configuration
project-prompt verify-api
```

**Alternative: Manual .env setup**
1. Create `.env` file in your project root
2. Add: `anthropic_API=your_key_here`
3. Ensure `.env` is in `.gitignore`
4. Run `project-prompt verify-api`

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
