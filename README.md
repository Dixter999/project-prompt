# ProjectPrompt v2.0

🤖 **AI-powered project analysis and improvement suggestions**

Transform your codebase with intelligent analysis and personalized AI recommendations.

---

## ⚡ Quick Reference Card

**Four Simple Commands - Always run in YOUR project directory (not ProjectPrompt directory):**

```bash
# 1. Install once (in ProjectPrompt directory)
git clone https://github.com/Dixter999/project-prompt.git && cd project-prompt && pip install -e .
# ✅ Next: Navigate to your actual project

# 2. Analyze your project (in YOUR project directory)
cd /path/to/your/project && projectprompt analyze .
# ✅ Next: Check what groups were found

# 3. See what groups were found
projectprompt status
# ✅ Next: Pick a group and generate suggestions

# 4. Get AI suggestions for a group
projectprompt suggest "group_name"  # Use actual names from status
# ✅ Next: Review the suggestions file
```

**🔑 Optional: Add AI key for better suggestions**
```bash
# In ProjectPrompt directory, create .env file
cd /path/to/project-prompt && echo "ANTHROPIC_API_KEY=your_key" > .env
```

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

### Step 1: Install ProjectPrompt
```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
```
**✅ Next Step:** Set up API keys for AI suggestions (optional) or go straight to analyzing your project.

### Step 2: Set up API Keys (Optional - for AI suggestions)
```bash
# Create .env file in the ProjectPrompt installation directory
cd /path/to/project-prompt
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```
**✅ Next Step:** Navigate to your actual project directory (not the ProjectPrompt directory).

### Step 3: Analyze Your Project
```bash
# IMPORTANT: Navigate to YOUR project (the one you want to analyze)
cd /path/to/your/project
projectprompt analyze .
```
**✅ Next Step:** Check what groups were found with `projectprompt status`.

### Step 4: Check Analysis Results
```bash
projectprompt status
```
**✅ Next Step:** Pick a group from the list and generate suggestions with `projectprompt suggest "group_name"`.

### Step 5: Generate AI Suggestions
```bash
projectprompt suggest "core_modules"  # Use actual group names from status
```
**✅ Next Step:** Review the generated suggestions file or create suggestions for other groups.

---

## ⚠️ **Important: Where to Run Commands**

**Key Rule**: Always run `projectprompt` commands **inside the project you want to analyze**, not in the ProjectPrompt tool directory.

### ✅ **Correct Workflow with Next Steps**:
```bash
# 1. Install ProjectPrompt (one-time setup)
cd /path/to/project-prompt
pip install -e .
```
**✅ Next Step:** Navigate to your actual project directory.

```bash
# 2. Navigate to YOUR project (the one you want to analyze)
cd /path/to/your/actual/project
```
**✅ Next Step:** Run the analysis command.

```bash
# 3. Run analysis commands from YOUR project directory
projectprompt analyze .
```
**✅ Next Step:** Check what groups were found with `projectprompt status`.

```bash
projectprompt status
```
**✅ Next Step:** Generate suggestions for any group using `projectprompt suggest "group_name"`.

```bash
projectprompt suggest "group_name"    # Use actual group names from status
```
**✅ Next Step:** Open the generated suggestions file or analyze another group.

### ❌ **Common Mistake**:
```bash
# DON'T do this - running commands from ProjectPrompt directory
cd /path/to/project-prompt
projectprompt analyze .               # This analyzes the TOOL, not your project
```

### 📝 **Example Scenarios with Clear Steps**:

**Scenario 1: Analyzing a web app**
```bash
cd /home/user/my-web-app              # Go to your web app
```
**✅ Next Step:** Run the analysis.

```bash
projectprompt analyze .               # Analyze the web app
```
**✅ Next Step:** Check what groups were created.

```bash
projectprompt status                  # See: frontend_modules, backend_modules, etc.
```
**✅ Next Step:** Generate suggestions for the most important group.

```bash
projectprompt suggest "frontend_modules"  # Get suggestions for frontend
```
**✅ Next Step:** Review suggestions file or analyze backend_modules.

**Scenario 2: Analyzing a Python library**
```bash
cd /home/user/my-python-lib           # Go to your library
```
**✅ Next Step:** Analyze the project structure.

```bash
projectprompt analyze .               # Analyze the library
```
**✅ Next Step:** See what groups were detected.

```bash
projectprompt status                  # See: core_modules, utility_modules, etc.
```
**✅ Next Step:** Start with core modules for best impact.

```bash
projectprompt suggest "core_modules"  # Get suggestions for core code
```
**✅ Next Step:** Implement suggestions or analyze utility_modules.

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
│
└── 🗑️ uninstall
    ├── Purpose: Completely remove ProjectPrompt from your system
    ├── Options:
    │   ├── --force, -f                → Force uninstall without confirmation
    │   └── --keep-data                → Keep analysis data files (only remove tool)
    ├── Actions:
    │   ├── Removes the ProjectPrompt package
    │   ├── Cleans up analysis directories (optional)
    │   └── Shows manual cleanup instructions
    └── Example Results:
        ├── ✅ ProjectPrompt package uninstalled successfully
        ├── 🧹 Analysis directories removed
        └── 🎉 Complete removal from system
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
**✅ Next Step:** Run `projectprompt status` to confirm groups, then pick one to analyze with `projectprompt suggest "group_name"`.

### Example 2: Generate AI Suggestions

```bash
$ projectprompt suggest "core_modules" --detail-level detailed
🤖 Generating suggestions for group: core_modules
🔧 Using API: anthropic (detail level: detailed)
Generating suggestions  [####################################]  100%
✅ Suggestions created: project-prompt-output/suggestions/core_modules-suggestions.md
📄 45 lines of suggestions created
```
**✅ Next Step:** Open the suggestions file to review recommendations or generate suggestions for another group.

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
**✅ Next Step:** Generate suggestions for remaining groups or start implementing existing suggestions.

### Example 4: Advanced Analysis with Exclusions

```bash
$ projectprompt analyze . --max-files 100 --exclude "*.log" --exclude "node_modules" --output ./custom-output
🔍 Analyzing project: /mnt/h/Projects/my-project
📁 Output directory: ./custom-output
📊 Max files to analyze: 100
🚫 Excluding patterns: *.log, node_modules
Analyzing project  [####################################]  100%
✅ Analysis complete! Results saved to: ./custom-output
```
**✅ Next Step:** Run `projectprompt status --analysis-dir ./custom-output` to see the groups found.

---

## 🔧 Configuration

### API Keys Setup
The `.env` file should be created in the **ProjectPrompt installation directory** (where you ran `pip install -e .`):

```bash
# Navigate to ProjectPrompt installation directory
cd /path/to/project-prompt
```
**✅ Next Step:** Create the .env file with your API key.

```bash
# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your_anthropic_key_here" > .env
```
**✅ Next Step:** Verify the file was created with `cat .env`, then navigate to your project for analysis.

**Example .env file content:**
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

## 🚨 Quick Fixes for Common Issues

### "Not working?" - Run these 3 commands:
```bash
# 1. Check you're in the RIGHT directory (your project, not ProjectPrompt)
pwd  # Should show YOUR project path, not /path/to/project-prompt
```
**✅ Next Step:** If in wrong directory, navigate to your project with `cd /path/to/your/project`.

```bash
# 2. Check if analysis exists
projectprompt status  # Should show groups, not "not found"
```
**✅ Next Step:** If no groups found, run `projectprompt analyze .` first.

```bash
# 3. Use EXACT group names (copy-paste from status output)
projectprompt suggest "exact_group_name_from_status"
```
**✅ Next Step:** If still issues, check the detailed troubleshooting section below.

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

## 🆘 Troubleshooting

### Common Issues and Solutions

#### ❌ "Group 'core_modules' not found"
**Problem**: The group you're trying to analyze doesn't exist in your project.

**Solution**: 
```bash
# Check what groups are actually available
projectprompt status
```
**✅ Next Step:** Use one of the actual group names shown in the output.

```bash
# Use the actual group names shown
projectprompt suggest "actual_group_name"
```
**✅ Next Step:** Review the generated suggestions file.

#### ❌ "Analysis directory not found"
**Problem**: You're running commands in a directory that hasn't been analyzed yet.

**Solution**:
```bash
# First analyze the project
projectprompt analyze .
```
**✅ Next Step:** Check the analysis results.

```bash
# Then run other commands
projectprompt status
```
**✅ Next Step:** Generate suggestions for a group.

```bash
projectprompt suggest "group_name"
```
**✅ Next Step:** Review the suggestions file.

#### ❌ "Anthropic API key not found"
**Problem**: API key not configured or not in the right location.

**Solution**:
```bash
# Create .env file in ProjectPrompt installation directory
cd /path/to/project-prompt  # Where you installed ProjectPrompt
echo "ANTHROPIC_API_KEY=your_actual_key" > .env
```
**✅ Next Step:** Verify the file was created correctly.

```bash
# Verify the file exists
cat .env
```
**✅ Next Step:** Navigate back to your project and try generating suggestions again.

#### ❌ "Running in test mode"
**Status**: This is normal when no API key is configured. You'll get basic suggestions without AI.

**To enable AI**: Follow the API key setup instructions above.

### Quick Diagnostic Commands
```bash
# Check if ProjectPrompt is installed correctly
projectprompt --help
```
**✅ Next Step:** If help shows, installation is working. Check your current location.

```bash
# Check current directory and existing analysis
pwd
ls -la project-prompt-output/ 2>/dev/null || echo "No analysis found"
```
**✅ Next Step:** If no analysis found, run `projectprompt analyze .` to create one.

```bash
# Check what groups are available
projectprompt status
```
**✅ Next Step:** Use the group names shown to generate suggestions.

---

## 📚 Usage Examples

### Example 1: First-Time Setup and Analysis
```bash
# Step 1: Install ProjectPrompt (one-time)
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
```
**✅ Next Step:** Set up API key for AI features (optional).

```bash
# Step 2: Set up API key (optional, one-time)
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```
**✅ Next Step:** Navigate to your actual project directory.

```bash
# Step 3: Analyze your actual project
cd /path/to/your/web/app  # Navigate to YOUR project
projectprompt analyze .   # Analyze current directory
```
**✅ Next Step:** Check what groups were created.

```bash
# Step 4: Check what was found
projectprompt status      # Shows available groups
```
**✅ Next Step:** Pick a group and generate AI suggestions.

```bash
# Step 5: Get AI suggestions
projectprompt suggest "frontend_modules"  # Use actual group names
```
**✅ Next Step:** Review the suggestions file and implement recommendations.

### Example 2: Different Project Types
```bash
# Python Library Analysis
cd /home/user/my-python-lib
projectprompt analyze .
```
**✅ Next Step:** Check groups with `projectprompt status`.

```bash
projectprompt suggest "core_modules"
```
**✅ Next Step:** Review suggestions or analyze other groups.

```bash
# Web App Analysis  
cd /home/user/my-react-app
projectprompt analyze .
```
**✅ Next Step:** See what groups were detected.

```bash
projectprompt suggest "frontend_modules"
```
**✅ Next Step:** Implement frontend suggestions or analyze backend.

```bash
# Data Science Project
cd /home/user/ml-project
projectprompt analyze .
```
**✅ Next Step:** Check available groups for data projects.

```bash
projectprompt suggest "data_processing"
```
**✅ Next Step:** Apply data optimization suggestions.

### Example 3: Large Project with Limits
```bash
# Navigate to your large project first
cd /path/to/large/project
```
**✅ Next Step:** Run analysis with custom settings.

```bash
# Analyze with custom settings
projectprompt analyze . \
  --max-files 2000 \
  --output ./project-analysis \
  --exclude "vendor/*" \
  --exclude "*.min.js"
```
**✅ Next Step:** Check the custom output directory with `projectprompt status --analysis-dir ./project-analysis`.

### Example 4: AI-Powered Code Review
```bash
# Navigate to your project first
cd /path/to/your/project
```
**✅ Next Step:** Generate detailed suggestions for core modules.

```bash
# Get detailed suggestions for core modules
projectprompt suggest "core_modules" \
  --detail-level detailed \
  --api anthropic
```
**✅ Next Step:** Review the detailed suggestions, then get quick wins for utilities.

```bash
# Get quick wins for utility modules  
projectprompt suggest "utility_modules" \
  --detail-level basic
```
**✅ Next Step:** Implement the basic suggestions first, then tackle the detailed ones.

### Example 5: Team Workflow
```bash
# 1. Team lead sets up ProjectPrompt (one-time)
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
echo "ANTHROPIC_API_KEY=team_key" > .env
```
**✅ Next Step:** Navigate to the team project and analyze it.

```bash
# 2. Team lead analyzes the team's project
cd /path/to/our-team-project  # Navigate to actual project
projectprompt analyze . --max-files 1500
```
**✅ Next Step:** Check what groups were created and assign them to developers.

```bash
# 3. Developers work on different modules (all from project directory)
# Still in /path/to/our-team-project:
projectprompt suggest "feature_modules" --detail-level medium
```
**✅ Next Step:** Generate suggestions for test modules.

```bash
projectprompt suggest "test_modules" --detail-level basic
```
**✅ Next Step:** Review progress and coordinate implementation.

```bash
# 4. Review what's been done
projectprompt status
```
**✅ Next Step:** Distribute suggestions files to team members and track implementation progress.

---

## 🗑️ Uninstalling ProjectPrompt

### Simple Uninstall
```bash
projectprompt uninstall
```
**✅ Next Step:** Confirm the removal when prompted. Your analysis data will be cleaned up too.

### Force Uninstall (No Prompts)
```bash
projectprompt uninstall --force
```
**✅ Next Step:** ProjectPrompt will be removed immediately without confirmation.

### Keep Analysis Data
```bash
projectprompt uninstall --keep-data
```
**✅ Next Step:** Only the tool is removed, your project analysis files are preserved.

### What Gets Removed:
- ✅ ProjectPrompt package and command
- ✅ Analysis directories (`project-prompt-output/`) in current path
- ✅ Shows locations of API key files for manual cleanup
- ✅ Verification that uninstall completed successfully

### Manual Cleanup (if needed):
If you installed from source, you may also need to:
```bash
# Remove the source directory
rm -rf /path/to/project-prompt

# Remove API key files
rm /path/to/project-prompt/.env

# Find any remaining analysis directories
find ~ -name 'project-prompt-output' -type d
```
**✅ Next Step:** Restart your terminal to ensure the command is fully removed.

---

## 📝 Summary: Remember These Key Points

### 🎯 **Most Important Rule**
Always run `projectprompt` commands **in your project directory**, not in the ProjectPrompt installation directory.

### 🔄 **Basic Workflow (4 Steps)**
1. **Install once**: `git clone + pip install -e .` (in ProjectPrompt directory)
2. **Navigate**: `cd /path/to/your/project` (to YOUR project)
3. **Analyze**: `projectprompt analyze .` (creates groups)
4. **Suggest**: `projectprompt suggest "group_name"` (generates AI recommendations)

### 🚨 **When Something Goes Wrong**
1. Check you're in the right directory: `pwd`
2. Check if analysis exists: `projectprompt status`
3. Use exact group names from status output

### 🔑 **For AI Suggestions**
- Optional but recommended: Add API key in ProjectPrompt directory
- Create `.env` file: `echo "ANTHROPIC_API_KEY=your_key" > .env`

### 📁 **What You Get**
- Analysis files in `project-prompt-output/analysis/`
- AI suggestions in `project-prompt-output/suggestions/`
- Your original files are never modified

---

## 📖 Need Help?

```bash
projectprompt --help                 # General help
projectprompt analyze --help         # Analyze command help
projectprompt suggest --help         # Suggest command help
```

---

**Made with ❤️ for developers who want to improve their code with AI assistance**
