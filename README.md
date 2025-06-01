# ProjectPrompt

![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.2.8-green)](https://github.com/Dixter999/project-prompt/releases)

**ProjectPrompt** is an intelligent CLI tool that analyzes code projects and provides AI-powered insights, documentation generation, and improvement suggestions. It helps developers understand their codebase structure, generate contextual prompts, and maintain better project documentation.

## ✨ Key Features

- **🔍 Smart Project Analysis**: Automatically detects technologies, frameworks, and project structure
- **🤖 AI-Powered Insights**: Integration with Anthropic Claude and OpenAI for intelligent code analysis
- **📋 AI Rules Generation**: Automatically generate development rules based on project patterns and best practices
- **📊 Visual Dashboards**: Generate comprehensive project dashboards in HTML or Markdown
- **🔗 Dependency Analysis**: Advanced dependency mapping with functional groups
- **🌐 Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, and more
- **⚡ Offline Capable**: Core features work without internet, AI features require API keys
- **📋 Progress Tracking**: Track development progress across project phases
- **🎯 Contextual Prompts**: Generate targeted prompts for specific functionalities

## 🚀 Quick Start

### Installation

```bash
pip install projectprompt
```

### Verify Installation

```bash
project-prompt version
```

### Basic Usage

```bash
# Analyze your current project
project-prompt analyze

# Generate a project dashboard
project-prompt dashboard

# Get help with all commands
project-prompt help
```

## 📖 Installation Guide

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Standard Installation

```bash
pip install projectprompt
```

### Development Installation

```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -r requirements.txt
```

### Troubleshooting Installation

If you encounter `command not found` errors:

**For zsh users:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For bash users:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Alternative: Run via Python module**
```bash
python -m src.main version
```

**Create convenient alias**
```bash
echo 'alias pp="project-prompt"' >> ~/.zshrc
source ~/.zshrc
# Now use: pp analyze, pp dashboard, etc.
```

## 🎯 What to Expect

When you run ProjectPrompt on your project, you can expect:

### Immediate Results
- **Project structure analysis** with file counts and organization
- **Technology detection** for languages, frameworks, and tools
- **Basic dependency mapping** showing relationships between files
- **Code quality metrics** including complexity analysis

### With AI APIs Configured
- **Intelligent insights** about your codebase architecture
- **Improvement suggestions** tailored to your project
- **Code explanations** for complex functions
- **Refactoring recommendations** with best practices

### Premium Features
- **Advanced dashboards** with interactive visualizations
- **Comprehensive dependency analysis** with functional groupings
- **Implementation assistants** for new features
- **Progress tracking** across development phases

## 🗺️ Interactive Command Mind Map

Explore our comprehensive **[Command Mind Map](docs/COMMAND_MINDMAP.md)** - a visual overview of all **35+ verified commands** organized by category. This interactive diagram helps you discover functionality and understand command relationships.

![Command Overview](https://img.shields.io/badge/Commands-35+-blue) ![Categories](https://img.shields.io/badge/Categories-8-green) ![Interactive](https://img.shields.io/badge/Map-Interactive-purple) ![Status](https://img.shields.io/badge/Status-Verified-brightgreen)

### 🎯 How to View the Interactive Mind Map

**Option 1: VS Code Extension (Recommended)**
```bash
# Install the Markmap extension in VS Code
code --install-extension gera2ld.markmap-vscode
# Then open docs/COMMAND_MINDMAP.md in VS Code
```

**Option 2: Online Viewer**
1. Copy the content from [docs/COMMAND_MINDMAP.md](docs/COMMAND_MINDMAP.md)
2. Paste it into the [Markmap REPL](https://markmap.js.org/repl)
3. Enjoy the interactive navigation!

**Option 3: Quick Command Reference**
For a text-based overview, see the [Command Reference](#%EF%B8%8F-command-reference) section below.

## 🛠️ Command Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze project structure and generate insights | `project-prompt analyze` |
| `dashboard` | Generate visual project dashboard | `project-prompt dashboard --format html` |
| `version` | Show version and API status | `project-prompt version` |
| `help` | Display detailed help information | `project-prompt help` |
| `init` | Initialize project with ProjectPrompt | `project-prompt init` |
| `menu` | Launch interactive menu interface | `project-prompt menu` |

### API Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `set-api` | Configure API keys for AI services | `project-prompt set-api anthropic` |
| `verify-api` | Check API configuration status | `project-prompt verify-api` |
| `check-env` | Verify environment variables | `project-prompt check-env` |

### Project Analysis

| Command | Description | Example |
|---------|-------------|---------|
| `analyze-group` | Analyze specific functional groups | `project-prompt analyze-group "Authentication"` |
| `generate-suggestions` | Generate AI-powered improvement suggestions | `project-prompt generate-suggestions` |
| `track-progress` | Track development progress across phases | `project-prompt track-progress` |

### AI Features

| Command | Description | Example |
|---------|-------------|---------|
| `ai analyze` | AI-powered code analysis | `project-prompt ai analyze file.py` |
| `ai refactor` | Get refactoring suggestions | `project-prompt ai refactor file.py` |
| `ai explain` | Explain code functionality | `project-prompt ai explain file.py --detail advanced` |
| `ai generate` | Generate code or documentation | `project-prompt ai generate` |

### AI-Powered Rules Management 🤖

| Command | Description | Example |
|---------|-------------|---------|
| `rules suggest` | Generate AI-powered rule suggestions | `project-prompt rules suggest --ai --threshold 0.8` |
| `rules analyze-patterns` | Analyze project patterns for rules | `project-prompt rules analyze-patterns --detailed` |
| `rules generate-project-rules` | Generate clean project-rules.md format | `project-prompt rules generate-project-rules --ai` |
| `rules auto-generate` | Auto-generate complete rules files | `project-prompt rules auto-generate --output rules.yaml` |
| `rules generate-structured-rules` | **NEW**: Generate sophisticated structured rules | `project-prompt rules generate-structured-rules --ai` |
| `rules validate-structured-rules` | **NEW**: Validate structured YAML rules | `project-prompt rules validate-structured-rules rules.yaml` |

### Premium Features

| Command | Description | Example |
|---------|-------------|---------|
| `premium dashboard` | Advanced interactive dashboard | `project-prompt premium dashboard` |
| `premium implementation` | Implementation assistant | `project-prompt premium implementation "user auth"` |

### Utilities

| Command | Description | Example |
|---------|-------------|---------|
| `delete` | Clean up generated files | `project-prompt delete all --force` |
| `setup-alias` | Set up command aliases | `project-prompt setup-alias` |
| `setup-deps` | Install optional dependencies | `project-prompt setup-deps` |
| `set-log-level` | Change logging verbosity | `project-prompt set-log-level debug` |
| `diagnose` | Diagnose installation issues | `project-prompt diagnose` |

### Subscription Management

| Command | Description | Example |
|---------|-------------|---------|
| `subscription plans` | View available subscription plans | `project-prompt subscription plans` |
| `subscription activate` | Activate premium license | `project-prompt subscription activate LICENSE_KEY` |
| `subscription info` | View current subscription status | `project-prompt subscription info` |

### Telemetry

| Command | Description | Example |
|---------|-------------|---------|
| `telemetry enable` | Enable anonymous usage analytics | `project-prompt telemetry enable` |
| `telemetry disable` | Disable usage analytics | `project-prompt telemetry disable` |
| `telemetry status` | Check telemetry status | `project-prompt telemetry status` |

## 🔧 Configuration

### Environment Setup

Create a `.env` file in your project root:

```bash
# AI API Keys (optional but recommended)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GITHUB_TOKEN=your_github_token_here

# Logging level
LOG_LEVEL=info
```

### API Configuration

1. **Anthropic Claude** (Recommended):
   ```bash
   project-prompt set-api anthropic
   ```

2. **OpenAI GPT**:
   ```bash
   project-prompt set-api openai
   ```

3. **Verify Configuration**:
   ```bash
   project-prompt verify-api
   ```

## 📊 Output Examples

### Basic Analysis
```bash
project-prompt analyze
```
**Generates:**
- Project structure overview
- File type distribution
- Basic metrics and statistics
- Technology stack detection

### Dashboard Generation
```bash
project-prompt dashboard --format html --output ./report.html
```
**Creates:**
- Interactive HTML dashboard
- Dependency graphs
- Code quality metrics
- Navigation-friendly project overview

### AI-Powered Insights
```bash
project-prompt ai analyze src/main.py --output analysis.json
```
**Provides:**
- Code quality assessment
- Potential issues detection
- Improvement recommendations
- Security considerations

## 🎨 Use Cases

### For Individual Developers
- **Code Reviews**: Analyze code quality before commits
- **Documentation**: Generate comprehensive project documentation
- **Learning**: Understand complex codebases quickly
- **Refactoring**: Get AI suggestions for code improvements

### For Teams
- **Onboarding**: Help new team members understand project structure
- **Architecture**: Visualize system dependencies and relationships
- **Standards**: Maintain consistent code quality across projects
- **Planning**: Track development progress and milestones

### For Project Managers
- **Progress Tracking**: Monitor development phases and completion
- **Risk Assessment**: Identify potential technical debt
- **Resource Planning**: Understand project complexity and scope
- **Reporting**: Generate visual reports for stakeholders

## 🔒 Privacy & Security

- **Local Processing**: Core analysis runs entirely on your machine
- **API Usage**: AI features only send code snippets when explicitly requested
- **No Data Collection**: Your code never leaves your environment without consent
- **Optional Telemetry**: Anonymous usage statistics can be disabled anytime

## 🆘 Getting Help

### Command Help
```bash
project-prompt [COMMAND] --help
```

### Troubleshooting
```bash
project-prompt diagnose
```

### Interactive Menu
```bash
project-prompt menu
```

### Documentation
- **Quick Start**: `QUICKSTART_GUIDE.md`
- **User Guide**: `docs/guides/user_guide.md`
- **API Reference**: `docs/reference/api_reference.md`

## 🤖 AI-Powered Rules Management

ProjectPrompt includes sophisticated AI capabilities for automatic rule generation with advanced structured rule modeling:

### Smart Rule Suggestions
```bash
# Generate AI-powered development rules for your project
project-prompt rules suggest --ai --threshold 0.8

# Get detailed pattern analysis  
project-prompt rules analyze-patterns --detailed

# Generate a clean project-rules.md file
project-prompt rules generate-project-rules --ai --output project-rules.md

# NEW: Generate structured rules with sophisticated models
project-prompt rules generate-structured-rules --ai --confidence 0.7
```

### Structured Rules System 🏗️
The new structured rules system provides enterprise-grade rule management:

- **RuleSet**: Complete rule collections with versioning and metadata
- **RuleGroup**: Organized rule categories (Technology, Architecture, Security, etc.)
- **RuleItem**: Individual rules with priority, context, and examples
- **RuleContext**: File-specific targeting (extensions, directories, patterns)
- **YAML Export**: Professional rule documentation and sharing

### What You Get
- **Technology Detection**: Automatically identifies frameworks, tools, and patterns
- **Best Practice Suggestions**: AI-generated rules based on industry standards  
- **Confidence Scoring**: Each suggestion includes a confidence level (0.0-1.0)
- **Implementation Roadmap**: Prioritized phases for implementing suggested rules
- **Multiple Formats**: Structured YAML, Markdown reports, or JSON export
- **Context-Aware Rules**: File-specific rules with directory and pattern targeting
- **Rule Validation**: Built-in validation for structured rule files

### Example Output
```markdown
## Technology Constraints
### Mandatory Technologies
- **Python 3.8+**: Core language - follow PEP 8 standards and use type hints
- **Typer**: CLI framework for all command-line interfaces

### Architecture Rules
- All analysis classes MUST inherit from appropriate base classes
- Use lazy loading for expensive resources (AI clients, large models)

### Implementation Roadmap
### Phase 1: Critical Rules (Week 1-2)
- [ ] API Key Security Validation (Confidence: 1.0/1.0)
- [ ] File System Security (Confidence: 0.9/1.0)
```

## 🚀 Advanced Features

### Premium Capabilities
- Advanced dependency analysis with madge integration
- AI-powered implementation assistants
- Comprehensive progress tracking
- Priority support and updates

### Extensibility
- Custom analyzers for specific technologies
- Template system for output customization
- Plugin architecture for additional integrations
- API for programmatic access

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Dixter999/project-prompt/issues)
- **Documentation**: [Project Wiki](https://github.com/Dixter999/project-prompt/wiki)
- **Email**: daniel@lagowski.es

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to get started?** Run `project-prompt analyze` in your project directory and discover what ProjectPrompt can do for you!
