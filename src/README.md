# ProjectPrompt Source Code

This directory contains the source code for ProjectPrompt.

## Directory Structure

- **`analyzers/`**: Code for analyzing project structure, dependencies, and architecture
- **`api/`**: API interfaces and endpoints for integration with other systems
- **`core/`**: Core functionality including the main processing pipeline
- **`generators/`**: Modules for generating documentation and suggestions
- **`integrations/`**: Integrations with external services (AI models, VCS, etc.)
- **`templates/`**: Project templates and prompt templates
- **`ui/`**: User interface components
- **`utils/`**: Utility functions and helpers

## Key Files

- **`main.py`**: Entry point for the application
- **`__init__.py`**: Package initialization

## Module Dependencies

```
core → analyzers → integrations
  ↓
generators → templates
  ↓
api → ui
```

## Usage

The source code is organized to be modular and extensible. Each module has a specific responsibility and can be modified independently.

For development guidelines, see the [Development Guide](../docs/development/development_guide.md).
