# ProjectPrompt VS Code Extension

A VS Code extension for ProjectPrompt, an AI-powered project assistant that helps you analyze, document, and enhance your codebase.

## Features

- **Project Analysis**: Automatically analyze your project structure and codebase
- **Contextual Prompts**: Generate AI-ready prompts that include project context
- **Documentation Assistance**: Get help with documentation generation
- **Feature Detection**: Identify key features and components in your project

## Requirements

- VS Code 1.60.0 or higher
- Python 3.8 or higher (for full functionality)

## Installation

1. Install the extension from the VS Code Marketplace
2. Make sure the Python package `projectprompt` is installed (`pip install projectprompt`)
3. Open a project folder and use the commands from the Command Palette (Ctrl+Shift+P)

## Commands

- `ProjectPrompt: Show Panel` - Open the main ProjectPrompt panel
- `ProjectPrompt: Analyze Project` - Run a project analysis
- `ProjectPrompt: Generate Prompt` - Generate a contextual prompt for the current file or selection
- `ProjectPrompt: Show Documentation` - Show documentation for the current project

## Extension Settings

This extension contributes the following settings:

* `projectprompt.pythonPath`: Path to Python executable (automatic by default)
* `projectprompt.autoAnalyze`: Whether to analyze the project automatically when opening a folder

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
