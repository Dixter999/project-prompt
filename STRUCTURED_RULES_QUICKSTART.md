# 🚀 Structured Rules System - Quick Start Guide

## Overview

The ProjectPrompt Structured Rules System provides enterprise-grade rule management with AI-powered suggestions, sophisticated modeling, and professional documentation export.

## Quick Commands

### Generate Structured Rules
```bash
# Basic generation (recommended)
project-prompt rules generate-structured-rules

# AI-enhanced with confidence filtering
project-prompt rules generate-structured-rules --ai --confidence 0.8

# Specify project type for better targeting
project-prompt rules generate-structured-rules --type web_application

# Custom output file
project-prompt rules generate-structured-rules --output my_project_rules.yaml
```

### Validate Rules
```bash
# Validate a structured rules file
project-prompt rules validate-structured-rules rules.yaml

# Detailed validation output
project-prompt rules validate-structured-rules rules.yaml --verbose
```

## What You Get

### Rule Structure
- **RuleSet**: Complete rule collection with metadata
- **RuleGroup**: Organized categories (Technology, Architecture, Security, etc.)
- **RuleItem**: Individual rules with priority and context
- **RuleContext**: File-specific targeting (extensions, directories, patterns)

### Priority Levels
- **🔴 MANDATORY**: Critical rules that must be followed
- **🟡 RECOMMENDED**: Best practices that should be implemented  
- **🟢 OPTIONAL**: Nice-to-have improvements

### Categories
- **TECHNOLOGY**: Framework and language constraints
- **ARCHITECTURE**: Structural and design patterns
- **CODE_STYLE**: Formatting and style requirements
- **TESTING**: Test coverage and quality standards
- **SECURITY**: Security best practices
- **DOCUMENTATION**: Documentation requirements
- **PERFORMANCE**: Performance optimization rules

## Example Output

```yaml
name: my_project_rules
version: 1.0.0
description: AI-generated rules for My Project
metadata:
  generated_at: 2025-06-01T00:00:00
  project_type: cli_tool
  ai_enhanced: true

groups:
  - name: technology_constraints
    description: Technology stack requirements
    category: technology
    rules:
      - content: "Use Python 3.8+ for all development"
        priority: mandatory
        category: technology
        context:
          file_extensions: ['.py']
          directories: ['src/', 'tests/']
        tags: ['python', 'version']
        examples:
          - "requires-python = \">=3.8\""
```

## Advanced Usage

### Project Types
- `web_application` - React, Vue, Angular, Flask, Django apps
- `data_science` - Jupyter, Pandas, NumPy, ML projects  
- `api_service` - FastAPI, Flask, REST API services
- `cli_tool` - Command-line applications
- `general` - Generic projects

### AI Enhancement
Set `ANTHROPIC_API_KEY` environment variable for AI-powered analysis:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
project-prompt rules generate-structured-rules --ai
```

### Integration with Existing Workflow
1. Generate rules for your project
2. Review and customize the YAML file
3. Share with your team
4. Use for code reviews and onboarding
5. Version control your rules files

## Demo Script

Run the comprehensive demonstration:
```bash
python demo_structured_rules_integration.py
```

This shows all features including rule creation, YAML export, filtering, and analysis capabilities.

---

**Ready to revolutionize your project's rule management!** 🎊
