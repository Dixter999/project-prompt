# ProjectPrompt v2.0

🤖 **AI-powered project analysis and improvement suggestions**

Transform your codebase with intelligent analysis and personalized AI recommendations.

---

## 🚀 Quick Start (2 minutes)

```bash
# 1. Clone and install
git clone https://github.com/your-username/projectprompt
cd projectprompt
pip install -e .

# 2. Configure API keys
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 3. Analyze your project
projectprompt analyze /path/to/your/project
projectprompt suggest "Core Files"
```

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
📁 Output directory: .
📊 Max files to analyze: 30
Analyzing project  [####################################]  100%
✅ Analysis complete! Results saved to: .
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
✅ Suggestions created: suggestions/core_modules-suggestions.md
📄 45 lines of suggestions created

📋 Suggestions preview:
────────────────────────────────────────
1. **Code Organization & Structure**
   - **Priority Level: High**
   - **Suggestion Title: Follow a Consistent Modular Architecture**
   - **Description and rationale:** A well-organized and modular codebase promotes 
     code reusability, maintainability, and scalability...
   - **Implementation steps:** Define a modular architecture that separates...
   - **Potential benefits:** Improved code organization, easier maintainability...

2. **Performance Optimizations**
   - **Priority Level: Medium**
   - **Suggestion Title: Implement Caching and Optimization Strategies**
   - **Description and rationale:** Caching frequently accessed data...
```

### Example 3: Check Project Status

```bash
$ projectprompt status
📊 Analysis Status for: .
==================================================
📁 Available groups (2):
   • core_modules
   • feature_modules

🤖 Created suggestions (1):
   • core_modules: suggestions/core_modules-suggestions.md

🚀 Next actions:
   Create suggestions with:
   • projectprompt suggest "feature_modules"
```

### Example 4: Advanced Analysis with Exclusions

```bash
$ projectprompt analyze . --max-files 100 --exclude "*.log" --exclude "node_modules" --output ./analysis-output
🔍 Analyzing project: /mnt/h/Projects/my-project
📁 Output directory: ./analysis-output
📊 Max files to analyze: 100
🚫 Excluding patterns: *.log, node_modules
Analyzing project  [####################################]  100%
✅ Analysis complete! Results saved to: ./analysis-output
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
├── analysis.json                    # Complete project analysis
├── groups/                          # Individual group files
│   ├── core_modules.json
│   └── feature_modules.json
└── suggestions/                     # AI-generated suggestions
    ├── core_modules-suggestions.md
    └── feature_modules-suggestions.md
```

---

## 🎯 What ProjectPrompt Analyzes

- **📂 Project Structure**: Files, directories, languages
- **🔍 Functional Groups**: Core modules, features, utilities, tests
- **📊 Code Organization**: Patterns, architecture, dependencies  
- **🚀 AI Suggestions**: Performance, security, maintainability
- **📈 Improvement Priorities**: High/Medium/Low priority recommendations

---

## ⚡ Performance

- **Installation**: ~3 seconds
- **Analysis**: ~1-2 seconds for small projects  
- **AI Suggestions**: ~5-10 seconds per group
- **File Limit**: Up to 10,000 files supported

---

## 🛠️ Requirements

- **Python**: 3.8+
- **API Key**: Anthropic or OpenAI account
- **Dependencies**: Automatically installed (6 core packages)

---

## 📖 Need Help?

```bash
projectprompt --help                 # General help
projectprompt analyze --help         # Analyze command help
projectprompt suggest --help         # Suggest command help
```

---

**Made with ❤️ for developers who want to improve their code with AI assistance**
