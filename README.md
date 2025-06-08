# ProjectPrompt v2.0

🤖 **AI-powered project analysis and improvement suggestions**

Transform your codebase with intelligent analysis and personalized AI recommendations.

---

## 📦 Installation

### Method 1: Install from Source (Recommended)
```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
```

### Method 2: Local Development
```bash
cd /path/to/project-prompt
pip install -e .
```

### Method 3: Quick Development Setup
```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -r requirements.txt
```

---

## 🚀 Quick Start (2 minutes)

### 1. Install ProjectPrompt
```bash
# Clone and install from source
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .

# Or for local development
cd /path/to/project-prompt
pip install -e .
```

### 2. Set up API Keys (Optional - for AI suggestions)
```bash
# For AI-powered suggestions, configure your API key:
export ANTHROPIC_API_KEY="your_key_here"
# OR
export OPENAI_API_KEY="your_key_here"

# Alternatively, create a .env file:
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 3. Analyze Your Project
```bash
# Basic analysis (works without API keys)
projectprompt analyze /path/to/your/project

# View analysis results
projectprompt status

# Generate AI suggestions (requires API key)
projectprompt suggest "core_modules"
```

---

## 🆕 What's New in v2.0

- **🔥 .gitignore Support**: Automatically respects your .gitignore patterns
- **🌍 English Interface**: Complete professional English translation
- **⚡ Performance**: 50% faster scanning with intelligent file filtering
- **🎯 Better Grouping**: Improved functional group detection
- **📱 Clean CLI**: Simplified, intuitive command structure

---

## 📋 Command Reference Mindmap

```
ProjectPrompt CLI
├── 🔍 analyze <path>
│   ├── Purpose: Scan project structure and create functional groups
│   ├── Options:
│   │   ├── --output, -o <dir>     → Output directory (default: project-output)
│   │   ├── --max-files, -m <num>  → Max files to analyze (default: 1000)
│   │   └── --exclude, -e <pattern> → Patterns to exclude (repeatable)
│   ├── Output: Analysis files + functional groups
│   └── Example Results:
│       ├── 📊 Found 2 functional groups:
│       ├── ┌─────────────────────────────┬───────────┐
│       ├── │ Group Name                  │ Files     │
│       ├── ├─────────────────────────────┼───────────┤
│       ├── │ core_modules                │         4 │
│       ├── │ feature_modules             │        21 │
│       └── └─────────────────────────────┴───────────┘
│
├── 🤖 suggest <group_name>
│   ├── Purpose: Generate AI-powered improvement suggestions for a specific group
│   ├── Options:
│   │   ├── --analysis-dir, -a <dir>    → Analysis directory (default: project-output)
│   │   ├── --api, -p <provider>        → AI provider (anthropic|openai)
│   │   ├── --detail-level, -d <level>  → Detail level (basic|medium|detailed)
│   │   └── --save-prompt, -s           → Save the generated prompt to file
│   ├── Output: AI suggestions markdown file
│   └── Example Results:
│       ├── ✅ Suggestions created: suggestions/core_modules-suggestions.md
│       ├── 📄 45 lines of suggestions created
│       └── 📋 AI-generated improvements with priorities and implementation steps
│
├── 📊 status
│   ├── Purpose: Show current analysis status and available groups
│   ├── Options:
│   │   └── --analysis-dir, -a <dir>    → Analysis directory to check
│   ├── Output: Status overview
│   └── Example Results:
│       ├── 📁 Available groups (2): core_modules, feature_modules
│       ├── 🤖 Created suggestions (1): core_modules
│       └── 🚀 Next actions: suggest commands for remaining groups
│
└── 🧹 clean
    ├── Purpose: Clean analysis data and start fresh
    ├── Options:
    │   └── --analysis-dir, -a <dir>    → Analysis directory to clean
    ├── Output: Removes analysis files
    └── Confirmation: Requires user confirmation before deletion
```

---

## 💡 Real Usage Examples

### Example 1: Analyze a Python Project

```bash
$ projectprompt analyze . --max-files 30
🔍 Analyzing project: /mnt/h/Projects/project-prompt
📁 Output directory: ./project-prompt-output
📊 Max files to analyze: 30
Analyzing project  [####################################]  100%
✅ Analysis complete! Results saved to: ./project-prompt-output
📊 Found 2 functional groups:
┌─────────────────────────────┬───────────┐
│ Group Name                  │ Files     │
├─────────────────────────────┼───────────┤
│ core_modules                │         4 │
│ feature_modules             │        21 │
└─────────────────────────────┴───────────┘

🚀 Next steps:
   Choose a group to analyze with AI:
   • projectprompt suggest "core_modules"
   • projectprompt suggest "feature_modules"
```

### Example 2: Generate AI Suggestions

```bash
$ projectprompt suggest "core_modules" --detail-level detailed
🤖 Generating suggestions for group: core_modules
🔧 Using API: anthropic (detail level: detailed)
Generating suggestions  [####################################]  100%
✅ Suggestions created: project-prompt-output/suggestions/core_modules-suggestions.md
📄 45 lines of suggestions created

📋 Suggestions preview:
────────────────────────────────────────
### 1. Organización y Estructura del Código ✅
- **Branch**: `refactor/modular-architecture`
- **Descripción**: Implementar arquitectura modular consistente que separe responsabilidades
- **Archivos a modificar/crear**:
  - `src/core/base.py` - Crear clases base comunes ✅
  - `src/interfaces/` - Definir interfaces claras ✅
- **Librerías/Herramientas a utilizar**:
  - `abc` - Clases abstractas para interfaces ✅
  - `typing` - Annotations de tipos ✅
- **Pasos a seguir**:
  1. Definir arquitectura modular que separe responsabilidades
  2. Crear interfaces claras entre módulos
  3. Implementar clases base comunes

### 2. Optimizaciones de Rendimiento ✅
- **Branch**: `optimize/caching-strategies`
- **Descripción**: Implementar estrategias de caché para datos accedidos frecuentemente
```

### Example 3: Check Project Status

```bash
$ projectprompt status
📊 Analysis Status for: ./project-prompt-output
==================================================
📁 Available groups (2):
   • core_modules
   • feature_modules

🤖 Created suggestions (1):
   • core_modules: project-prompt-output/suggestions/core_modules-suggestions.md

🚀 Next actions:
   Create suggestions with:
   • projectprompt suggest "feature_modules"
```

### Example 4: Advanced Analysis with Exclusions

```bash
$ projectprompt analyze . --max-files 100 --exclude "*.log" --exclude "node_modules" --output ./project-prompt-output
🔍 Analyzing project: /mnt/h/Projects/my-project
📁 Output directory: ./project-prompt-output
📊 Max files to analyze: 100
🚫 Excluding patterns: *.log, node_modules
Analyzing project  [####################################]  100%
✅ Analysis complete! Results saved to: ./project-prompt-output
```

---

## 🔧 Configuration

### API Keys (Required)
Add your API key to `.env` file:

```bash
# Choose one AI provider
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional settings
LOG_LEVEL=info
```

### Supported AI Providers
- **Anthropic Claude** (recommended): Fast, detailed analysis
- **OpenAI GPT**: Alternative provider with different perspective

---

## 📁 Output Structure

```
your-project/
├── [user files - UNTOUCHED]
└── project-prompt-output/           # ← All outputs here
    ├── analysis/
    │   ├── project-structure.md
    │   ├── dependency-map.md
    │   └── functional-groups/
    │       ├── core-analysis.md
    │       ├── ui-analysis.md
    │       └── utils-analysis.md
    └── suggestions/
        ├── fase-1-core.md
        ├── fase-2-integraciones.md
        └── fase-3-optimizaciones.md
```

---

## 🎯 Key Features

### 🔍 Smart Project Analysis
- **Respects .gitignore**: Automatically ignores files per your .gitignore patterns
- **Language Detection**: Identifies main programming languages and frameworks
- **Functional Grouping**: Organizes files into logical groups (core, features, utils, tests)
- **Project Type Detection**: Recognizes APIs, web apps, CLI tools, and libraries

### 🤖 AI-Powered Suggestions
- **Multiple AI Providers**: Support for Anthropic Claude and OpenAI GPT
- **Detailed Recommendations**: Get specific improvement suggestions with implementation steps
- **Priority-Based**: Suggestions ranked by impact and effort
- **Action-Oriented**: Clear next steps with branch names and file modifications

### 📊 Comprehensive Analysis
- **Project Structure**: Visual file organization and architecture overview
- **Dependency Mapping**: Internal and external dependency analysis
- **Code Metrics**: File counts, sizes, and language distribution
- **Export Options**: Markdown reports and JSON data for integration

---

## 🔧 Configuration Options

### Environment Variables
```bash
# AI Provider Configuration
ANTHROPIC_API_KEY=your_anthropic_key     # For Claude AI suggestions
OPENAI_API_KEY=your_openai_key          # For GPT AI suggestions

# Analysis Settings
PROJECTPROMPT_MAX_FILES=1000            # Maximum files to analyze
PROJECTPROMPT_OUTPUT_DIR=project-output  # Default output directory
```

### Command Options
```bash
# Analysis options
projectprompt analyze . \
  --max-files 500 \                     # Limit file count
  --output ./my-analysis \              # Custom output directory
  --exclude "*.log" \                   # Exclude patterns
  --exclude "temp/*"                    # Multiple exclusions

# Suggestion options  
projectprompt suggest "core_modules" \
  --api anthropic \                     # Choose AI provider
  --detail-level detailed \             # basic|medium|detailed
  --save-prompt                         # Save prompt for review
```

---

## 🛠️ Requirements

- **Python**: 3.8+ (3.10+ recommended)
- **Dependencies**: Automatically installed via pip
- **API Key**: Optional - only needed for AI suggestions
  - Anthropic Claude (recommended): Get key at [console.anthropic.com](https://console.anthropic.com)
  - OpenAI GPT: Get key at [platform.openai.com](https://platform.openai.com)

### Core Dependencies
```
click>=8.0.0
rich>=12.0.0
pathlib
typing-extensions
python-dotenv
anthropic (optional)
openai (optional)
```

---

## 🚫 What Gets Ignored

ProjectPrompt automatically respects your `.gitignore` files and includes these default patterns:

```bash
# Python
__pycache__/
*.pyc, *.pyo, *.pyd
.Python
*.so

# Node.js  
node_modules/
.npm

# Build outputs
build/
dist/

# Environment files
.env
.env.local

# System files
.DS_Store
Thumbs.db

# Version control
.git/
.svn/
.hg/

# Logs
*.log
```

---

## 📚 Usage Examples

### Example 1: Quick Analysis
```bash
# Analyze current directory
projectprompt analyze .

# Check what was found
projectprompt status
```

### Example 2: Large Project with Limits
```bash
# Analyze with file limit and custom output
projectprompt analyze /path/to/large/project \
  --max-files 2000 \
  --output ./project-analysis \
  --exclude "vendor/*" \
  --exclude "*.min.js"
```

### Example 3: AI-Powered Code Review
```bash
# Get detailed suggestions for core modules
projectprompt suggest "core_modules" \
  --detail-level detailed \
  --api anthropic

# Get quick wins for utility modules  
projectprompt suggest "utility_modules" \
  --detail-level basic
```

### Example 4: Team Workflow
```bash
# 1. Team lead analyzes project
projectprompt analyze ./our-project --max-files 1500

# 2. Developers get targeted suggestions
projectprompt suggest "feature_modules" --detail-level medium
projectprompt suggest "test_modules" --detail-level basic

# 3. Review what's been done
projectprompt status
```

---

## 📖 Need Help?

```bash
projectprompt --help                 # General help
projectprompt analyze --help         # Analyze command help
projectprompt suggest --help         # Suggest command help
```

---

**Made with ❤️ for developers who want to improve their code with AI assistance**
