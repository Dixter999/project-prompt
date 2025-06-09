# ProjectPrompt v2.0

🤖 **AI-powered project analysis and improvement suggestions**

Transform your codebase with intelligent analysis and personalized AI recommendations.

---

## ⚡ Quick Start in 5 Steps

**Always run commands in YOUR project directory (not ProjectPrompt directory):**

```bash
# 1. Install once (in ProjectPrompt directory)
git clone https://github.com/Dixter999/project-prompt.git && cd project-prompt && pip install -e .

# 2. Navigate to your project (the one you want to analyze)
cd /path/to/your/project

# 3. Analyze your project structure
projectprompt analyze .

# 4. Check what groups were found
projectprompt status

# 5. Get AI suggestions for a group
projectprompt suggest "group_name"  # Use actual names from status

# 6. Generate implementation prompts (NEW!)
projectprompt generate-prompts "group_name"  # Creates ready-to-use prompts

# 7. AI-driven implementation (NEWEST!)
projectprompt adaptive-implement "Add user authentication"  # Direct AI implementation
```

**🔑 Optional: Add AI key for better suggestions**
```bash
# In ProjectPrompt directory, create .env file
cd /path/to/project-prompt && echo "ANTHROPIC_API_KEY=your_key" > .env
```

### Example: Analyzing a Web App

```bash
# Step 1: Install (one-time)
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .

# Step 2: Navigate to your web app
cd /home/user/my-web-app

# Step 3: Analyze it
projectprompt analyze .
# Output: Found 3 groups: frontend_modules, backend_modules, utility_modules

# Step 4: Get AI suggestions for frontend
projectprompt suggest "frontend_modules"
# Output: Creates suggestions/frontend_modules-suggestions.md

# Step 5: Generate implementation prompts
projectprompt generate-prompts "frontend_modules"
# Output: Creates phase-by-phase prompts for AI assistants
```

---

## 📦 Installation

### Simple Installation (Recommended)
```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
```

**Test Installation:**
```bash
projectprompt --help  # Should show command help
```

**If command not found, try:**
```bash
python -m src.cli --help  # Alternative way to run
```

---

## 🚀 Step-by-Step Guide for New Users

### 1. First-Time Setup (Do Once)

**Install ProjectPrompt:**
```bash
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .
```

**Optional - Set up AI key for better suggestions:**
```bash
# Stay in the project-prompt directory
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 2. Analyze Any Project

**Navigate to your actual project:**
```bash
# Example paths - use YOUR actual project path
cd /home/user/my-web-app          # For a web application
cd /Users/john/my-python-lib      # For a Python library  
cd C:\Projects\my-node-app        # For a Node.js project
```

**Run the analysis:**
```bash
projectprompt analyze .
```

**Example output:**
```
🔍 Analyzing project: /home/user/my-web-app
📊 Found 3 functional groups:
┌─────────────────────────────┬───────────┐
│ Group Name                  │ Files     │
├─────────────────────────────┼───────────┤
│ frontend_modules            │        15 │
│ backend_modules             │         8 │
│ utility_modules             │         4 │
└─────────────────────────────┴───────────┘
```

### 3. Check What Was Found

```bash
projectprompt status
```

**Example output:**
```
📊 Analysis Status
==================================================
📁 Available groups (3):
   • frontend_modules (15 files)
   • backend_modules (8 files)
   • utility_modules (4 files)

🚀 Next actions:
   Create suggestions with:
   • projectprompt suggest "frontend_modules"
   • projectprompt suggest "backend_modules"
   • projectprompt suggest "utility_modules"
```

### 4. Generate AI Suggestions

```bash
projectprompt suggest "frontend_modules"
```

**Example output:**
```
🤖 Generating suggestions for group: frontend_modules
✅ Suggestions created: project-prompt-output/suggestions/frontend_modules-suggestions.md
📄 42 lines of suggestions created
```

### 5. Generate Implementation Prompts (NEW!)

```bash
projectprompt generate-prompts "frontend_modules"
```

**Example output:**
```
🤖 Generating implementation prompts for: frontend_modules
✅ Generated 3 implementation prompts:
   • frontend_modules-phase1-prompt.md
   • frontend_modules-phase2-prompt.md  
   • frontend_modules-phase3-prompt.md
📁 Prompts saved to: project-prompt-output/prompts/
```

### 6. Use the Prompts with AI Assistants

1. Open any prompt file (e.g., `project-prompt-output/prompts/frontend_modules-phase1-prompt.md`)
2. Copy the entire content
3. Paste into Claude, ChatGPT, or your preferred AI assistant
4. Follow the AI's implementation guidance
5. Move to the next phase after testing

---

## 📁 Example File Paths and Outputs

### Common Project Locations
```bash
# Web applications
/home/user/my-react-app
/Users/developer/vue-project
C:\Projects\angular-app

# Python projects
/home/user/ml-project
/Users/dev/flask-api
C:\Code\django-blog

# Node.js projects  
/home/user/express-api
/Users/dev/next-app
C:\Development\electron-app
```

### Output Structure After Analysis
```
your-project/
├── [your files - never modified]
└── project-prompt-output/
    ├── analysis/
    │   ├── project-structure.md      # Project overview
    │   └── functional-groups/
    │       ├── frontend_modules-analysis.md
    │       └── backend_modules-analysis.md
    ├── suggestions/
    │   ├── frontend_modules-suggestions.md  # AI improvement ideas
    │   └── backend_modules-suggestions.md
    └── prompts/
        ├── frontend_modules-phase1-prompt.md  # Ready for AI assistants
        ├── frontend_modules-phase2-prompt.md
        └── backend_modules-phase1-prompt.md
```
---

## ⚠️ Important: Directory Rules

**Key Rule**: Always run `projectprompt` commands **inside the project you want to analyze**, not in the ProjectPrompt tool directory.

### ✅ Correct Way:
```bash
# 1. Install ProjectPrompt (do this once)
cd /path/to/project-prompt
pip install -e .

# 2. Navigate to YOUR project
cd /path/to/your/actual/project

# 3. Run commands from YOUR project directory
projectprompt analyze .
projectprompt status
projectprompt suggest "group_name"
```

### ❌ Common Mistake:
```bash
# DON'T do this - analyzing the tool instead of your project
cd /path/to/project-prompt
projectprompt analyze .  # This analyzes ProjectPrompt, not your project
```

---

## 🆕 What's New in v2.0

- **🚀 Adaptive Implementation System**: Complete AI-driven implementation with FASE 1 & FASE 2 modes
- **💬 ConversationManager**: Multi-turn conversation support with context tracking
- **🔀 Advanced Workflow**: Multi-request orchestration with dependency resolution
- **🤖 Implementation Prompts**: Generate ready-to-use prompts for AI assistants
- **🔥 .gitignore Support**: Automatically respects your .gitignore patterns  
- **🌍 English Interface**: Complete professional English translation
- **⚡ Performance**: 50% faster scanning with intelligent file filtering
- **🎯 Better Grouping**: Improved functional group detection
- **📱 Clean CLI**: Simplified, intuitive command structure

---

## 🚨 Quick Troubleshooting

### "Group not found" Error
```bash
# Check what groups actually exist
projectprompt status
# Use the exact group names shown in the output
```

### "Analysis directory not found" Error  
```bash
# First analyze your project
projectprompt analyze .
# Then run other commands
projectprompt status
```

### "API key not found" Warning
```bash
# In ProjectPrompt installation directory, create .env file
cd /path/to/project-prompt
echo "ANTHROPIC_API_KEY=your_key" > .env
```

### Command Not Found
```bash
# Try alternative way to run
python -m src.cli --help
```

---

## 📋 Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `analyze <path>` | Scan project and create groups | `projectprompt analyze .` |
| `status` | Show analysis status and groups | `projectprompt status` |
| `suggest <group>` | Generate AI improvement suggestions | `projectprompt suggest "core_modules"` |
| `generate-prompts <group>` | Create implementation prompts | `projectprompt generate-prompts "core_modules"` |
| `adaptive-implement <task>` | **NEW!** AI-driven implementation system | `projectprompt adaptive-implement "Add authentication"` |
| `clean` | Remove analysis data | `projectprompt clean` |

### Key Options
```bash
# Analysis options
--max-files 500              # Limit files analyzed
--output ./custom-dir        # Custom output directory
--exclude "*.log"           # Exclude file patterns

# Suggestion options
--api anthropic             # Choose AI provider (anthropic|openai)
--detail-level detailed     # Detail level (basic|medium|detailed)
--phase 2                   # Generate specific phase prompt only

# Adaptive Implementation options (NEW!)
--use-workflow              # Enable FASE 2 advanced workflow management
--conversation-mode         # Enable multi-turn conversation sessions
--max-requests 10           # Maximum API requests for complex tasks
--target quality            # Optimization target (speed|cost|quality|balanced)
--complexity complex        # Task complexity (simple|medium|complex|very_complex)
--task-type implementation  # Task type (implementation|analysis|debugging|optimization|testing)
```

---

## 💡 Usage Examples

### Example 1: Analyze a Python Project

```bash
$ projectprompt analyze . --max-files 30
🔍 Analyzing project: /home/user/my-python-lib
📊 Found 2 functional groups:
┌─────────────────────────────┬───────────┐
│ Group Name                  │ Files     │
├─────────────────────────────┼───────────┤
│ core_modules                │         4 │
│ feature_modules             │        21 │
└─────────────────────────────┴───────────┘

🚀 Next: Choose a group for AI analysis
```

### Example 2: Generate AI Suggestions

```bash
$ projectprompt suggest "core_modules" --detail-level detailed
🤖 Generating suggestions for group: core_modules
✅ Suggestions created: project-prompt-output/suggestions/core_modules-suggestions.md
📄 45 lines of suggestions created
```

### Example 3: Generate Implementation Prompts

```bash
$ projectprompt generate-prompts "core_modules"
🤖 Generating implementation prompts for: core_modules
✅ Generated 3 implementation prompts:
   • core_modules-phase1-prompt.md
   • core_modules-phase2-prompt.md
   • core_modules-phase3-prompt.md
📁 Prompts saved to: project-prompt-output/prompts/
```

### Example 4: Check Project Status

```bash
$ projectprompt status
📊 Analysis Status
==================================================
📁 Available groups (2): core_modules, feature_modules
🤖 Created suggestions (1): core_modules
🚀 Remaining: projectprompt suggest "feature_modules"
```

---

## 🚀 NEW: Adaptive Implementation System (FASE 2)

ProjectPrompt now includes an advanced AI-driven implementation system with two operational modes:

### 📋 FASE 1: Standard Implementation (Fast)
Single-request implementation for quick tasks and simple features.

```bash
# Standard implementation examples
projectprompt adaptive-implement "Add user authentication system"
projectprompt adaptive-implement "Fix login bug" --task-type debugging
projectprompt adaptive-implement "Optimize database queries" --target cost
```

### 🚀 FASE 2: Advanced Workflow Management (Comprehensive)
Multi-request intelligent orchestration for complex tasks with conversation support.

```bash
# Advanced workflow examples
projectprompt adaptive-implement "Refactor entire API" --use-workflow
projectprompt adaptive-implement "Complex feature implementation" \
  --use-workflow --conversation-mode --max-requests 10
projectprompt adaptive-implement "Large architectural changes" \
  --use-workflow --conversation-mode --complexity very_complex --target quality
```

### 🤖 ConversationManager Features
The ConversationManager enables intelligent multi-turn conversations:

- **Session Management**: Creates and tracks conversation sessions across multiple interactions
- **Context Accumulation**: Maintains context across conversation turns for better continuity
- **Analytics & Insights**: Provides conversation analytics and pattern identification
- **Metadata Tracking**: Preserves implementation metadata and progress tracking

### 💡 How to Work with FASE 2

#### 1. Simple Tasks (Use FASE 1)
```bash
# Quick implementations, bug fixes, simple features
projectprompt adaptive-implement "Add logging to user service" --target speed
```

#### 2. Complex Tasks (Use FASE 2)
```bash
# Multi-step implementations, architectural changes, large features
projectprompt adaptive-implement "Implement microservices architecture" \
  --use-workflow --max-requests 15 --complexity very_complex
```

#### 3. Interactive Development (Use Conversation Mode)
```bash
# Iterative development with context preservation
projectprompt adaptive-implement "Build complete authentication system" \
  --use-workflow --conversation-mode --max-requests 8
```

### 🔄 Workflow Process
1. **Context Analysis**: Intelligent project context building and analysis
2. **Prompt Enhancement**: Advanced prompt optimization for specific tasks
3. **Request Orchestration**: Multi-request coordination with dependency resolution
4. **Response Processing**: Content extraction and implementation plan generation
5. **Conversation Tracking**: Session management and context accumulation (if enabled)
6. **Results Integration**: Comprehensive output with analytics and next steps

### 📊 Performance Characteristics
| Task Type | Recommended Mode | Expected Time | API Requests |
|-----------|------------------|---------------|--------------|
| Bug fixes, simple features | FASE 1 | 2-5 seconds | 1 request |
| Medium features, refactoring | FASE 2 | 10-30 seconds | 2-5 requests |
| Complex features, architecture | FASE 2 + Conversation | 1-3 minutes | 5-15 requests |

### 🎯 Task Types and Targets
```bash
# Task types
--task-type implementation    # New features and functionality
--task-type analysis         # Code analysis and review
--task-type debugging        # Bug fixes and troubleshooting
--task-type optimization     # Performance and efficiency improvements
--task-type testing          # Test creation and validation

# Optimization targets
--target speed              # Fastest response, basic models
--target cost               # Cost-optimized models and parameters
--target quality            # Highest quality, advanced models
--target balanced           # Balance of speed, cost, and quality (default)
```

### 📁 Output Structure
FASE 2 creates comprehensive outputs:
```
project-prompt-output/adaptive-implementation/
├── workflow_YYYYMMDD_HHMMSS.json           # Complete workflow data
├── workflow_summary_YYYYMMDD_HHMMSS.md     # Human-readable summary
└── conversation_SESSION-ID_YYYYMMDD.json   # Conversation data (if enabled)
```

---

## 🔧 Configuration

### API Keys Setup
Create a `.env` file in the **ProjectPrompt installation directory**:

```bash
# Navigate to ProjectPrompt installation directory
cd /path/to/project-prompt

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your_anthropic_key_here" > .env
```

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

## 🆘 Troubleshooting

### Common Issues and Quick Fixes

#### ❌ "Group 'core_modules' not found"
```bash
# Check what groups are actually available
projectprompt status
# Use the exact group names shown in the output
projectprompt suggest "actual_group_name"
```

#### ❌ "Analysis directory not found"  
```bash
# First analyze the project
projectprompt analyze .
# Then run other commands
projectprompt status
projectprompt suggest "group_name"
```

#### ❌ "Anthropic API key not found"
```bash
# Create .env file in ProjectPrompt installation directory
cd /path/to/project-prompt
echo "ANTHROPIC_API_KEY=your_actual_key" > .env
# Verify the file exists
cat .env
```

#### ❌ Command not found
```bash
# Check if ProjectPrompt is installed correctly
projectprompt --help
# If that fails, try:
python -m src.cli --help
```

### Quick Diagnostic Commands
```bash
# Check current directory and existing analysis  
pwd
ls -la project-prompt-output/ 2>/dev/null || echo "No analysis found"
projectprompt status
```

---

## 🎯 Key Features

### 🔍 Smart Project Analysis
- **Respects .gitignore**: Automatically ignores files per your .gitignore patterns
- **Language Detection**: Identifies main programming languages and frameworks
- **Functional Grouping**: Organizes files into logical groups (core, features, utils, tests)

### 🤖 AI-Powered Suggestions
- **Multiple AI Providers**: Support for Anthropic Claude and OpenAI GPT
- **Detailed Recommendations**: Get specific improvement suggestions with implementation steps
- **Priority-Based**: Suggestions ranked by impact and effort

### 🤖 Implementation Prompt Generation (NEW!)
- **Ready-to-Use Prompts**: Generate detailed implementation prompts from suggestions
- **Phase-by-Phase**: Each suggestion phase gets its own detailed prompt
- **AI Assistant Ready**: Prompts optimized for use with Claude, ChatGPT, and other AI assistants

---

## 🚀 Complete Workflow: From Analysis to Implementation

### Step 1: One-Time Setup
```bash
# Install ProjectPrompt (do this once)
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt
pip install -e .

# Optional: Set up API key for better suggestions
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Step 2: Analyze Your Project
```bash
# Navigate to your actual project
cd /path/to/your/project

# Analyze the project structure
projectprompt analyze .

# Check what groups were created
projectprompt status
```

### Step 3: Generate AI Suggestions
```bash
# Generate suggestions for each group
projectprompt suggest "core_modules"
projectprompt suggest "feature_modules" 
```

### Step 4: Generate Implementation Prompts (NEW!)
```bash
# Generate ready-to-use prompts for AI assistants
projectprompt generate-prompts "core_modules"

# Or generate a specific phase prompt
projectprompt generate-prompts "core_modules" --phase 2
```

### Step 5: Implement with AI Assistants
1. Open: `project-prompt-output/prompts/core_modules-phase1-prompt.md`
2. Copy the prompt content
3. Paste into Claude, ChatGPT, or your preferred AI assistant
4. Follow the AI's step-by-step implementation guidance
5. Test and validate the implementation
6. Move to the next phase prompt

---

## 🗑️ Uninstalling

```bash
# Simple uninstall
projectprompt uninstall

# Force uninstall (no prompts)
projectprompt uninstall --force

# Keep analysis data
projectprompt uninstall --keep-data
```

---

## 📝 Summary

### 🎯 Most Important Rule
Always run `projectprompt` commands **in your project directory**, not in the ProjectPrompt installation directory.

### 🔄 Basic Workflow
1. **Install once**: `git clone + pip install -e .` (in ProjectPrompt directory)
2. **Navigate**: `cd /path/to/your/project` (to YOUR project)
3. **Analyze**: `projectprompt analyze .` (creates groups)
4. **Suggest**: `projectprompt suggest "group_name"` (generates AI recommendations)
5. **Generate prompts**: `projectprompt generate-prompts "group_name"` (creates implementation prompts)

### 🚨 When Something Goes Wrong
1. Check you're in the right directory: `pwd`
2. Check if analysis exists: `projectprompt status`
3. Use exact group names from status output

### 🔑 For AI Suggestions
- Optional but recommended: Add API key in ProjectPrompt directory
- Create `.env` file: `echo "ANTHROPIC_API_KEY=your_key" > .env`

---

## 📖 Need Help?

```bash
projectprompt --help                 # General help
projectprompt analyze --help         # Analyze command help
projectprompt suggest --help         # Suggest command help
projectprompt generate-prompts --help # Implementation prompts help
```

---

## 🔍 API Diagnostics & Monitoring

ProjectPrompt includes a comprehensive diagnostic system to verify and monitor API usage:

### Quick Health Check
```bash
# Fast diagnostic (essential checks only)
projectprompt diagnose-api --quick

# Full diagnostic report
projectprompt diagnose-api

# Save detailed report to file
projectprompt diagnose-api --save-report api_health_report.json
```

### Diagnostic Features
✅ **API Key Configuration** - Validates ANTHROPIC_API_KEY format and availability
✅ **API Connectivity** - Tests actual connection to Anthropic API
✅ **Component Verification** - Checks all FASE 1 & FASE 2 components
✅ **Performance Metrics** - Monitors response times and success rates
✅ **Cost Tracking** - Real-time tracking of daily/monthly API costs
✅ **Cache Status** - Verifies caching system functionality
✅ **End-to-End Testing** - Complete workflow validation

### Real-Time Monitoring
```bash
# Monitor API usage in real-time
python scripts/api_monitor.py monitor

# Monitor for specific duration (30 minutes)
python scripts/api_monitor.py monitor --duration 30

# Save monitoring report
python scripts/api_monitor.py monitor --save-report monitoring_report.json

# Performance testing
python scripts/api_monitor.py test --requests 10
```

### Sample Diagnostic Output
```
🔍 Iniciando diagnóstico completo del sistema API...
✅ API Key Configuration: API key configurada correctamente
✅ API Connectivity: Conectividad con Anthropic API exitosa
✅ FASE 1 Components: Todos los componentes FASE 1 disponibles y funcionales
✅ FASE 2 Components: Componentes FASE 2 disponibles y funcionales
✅ Performance Metrics: Sistema funcionando correctamente
✅ Cost Tracking: Sistema de seguimiento de costos funcional
✅ Cache Status: Sistema de cache funcional
✅ Basic Request Test: Prueba de request completo exitosa

============================================================
📊 REPORTE FINAL DE SALUD DEL SISTEMA API
============================================================
🏥 Estado General: SALUDABLE
🔑 API Key: PASS
🌐 Conectividad: PASS
💰 Análisis de Costos:
   • daily_cost: $0.0000
   • monthly_cost: $0.0000
💡 Recomendaciones:
   ✅ Sistema API configurado correctamente
   🚀 Sistema listo para uso en producción
```

### Troubleshooting Common Issues
```bash
# No API key found
export ANTHROPIC_API_KEY="your-key-here"
# or create .env file in ProjectPrompt directory

# Component verification failed
pip install -e . --force-reinstall

# Connectivity issues
projectprompt diagnose-api  # Check detailed error messages
```

For detailed diagnostic information, see [API Verification Guide](docs/API_VERIFICATION_GUIDE.md).
