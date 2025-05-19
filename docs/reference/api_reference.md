# Project-Prompt API Reference

This document provides a reference for the Project-Prompt API classes and methods.

## Core Classes

### ProjectScanner

The `ProjectScanner` class scans and analyzes project structure.

```python
from src.analyzers.project_scanner import get_project_scanner

# Create scanner with default settings
scanner = get_project_scanner()

# Create scanner with custom settings
scanner = get_project_scanner(max_file_size_mb=10, max_files=1000)

# Scan a project
project_data = scanner.scan_project("/path/to/project")
```

**Key Methods:**
- `scan_project(project_path)`: Scans a project and returns analysis data
- `get_project_stats(project_data)`: Gets statistics about the project
- `get_file_content(file_path, max_size_mb=5)`: Gets file content with size limitation

### ProjectStructure

The `ProjectStructure` class manages project structure and configuration.

```python
from src.utils.project_structure import get_project_structure

# Get project structure instance for a specific project
structure = get_project_structure("/path/to/project")

# Create project structure
result = structure.create_structure()

# Get structure information
info = structure.get_structure_info()
```

**Key Methods:**
- `create_structure(overwrite=False)`: Creates or updates project structure
- `get_structure_info()`: Gets information about the project structure
- `save_analysis(content, metadata=None)`: Saves analysis content
- `save_prompt(content, metadata=None)`: Saves prompt content

### FunctionalityDetector

The `FunctionalityDetector` class detects project functionalities.

```python
from src.analyzers.functionality_detector import get_functionality_detector

# Create detector with default settings
detector = get_functionality_detector()

# Detect functionalities
functionalities = detector.detect_functionalities("/path/to/project")
```

**Key Methods:**
- `detect_functionalities(project_path)`: Detects functionalities in a project
- `analyze_project_files(files)`: Analyzes project files for functionalities
- `get_functionality_score(functionality, evidence)`: Calculates confidence score

## Generator Classes

### ContextualPromptGenerator

The `ContextualPromptGenerator` class generates contextual prompts.

```python
from src.generators.contextual_prompt_generator import get_contextual_prompt_generator

# Create generator
generator = get_contextual_prompt_generator()

# Generate prompt
prompt = generator.generate_prompt(project_data, functionality="auth")
```

**Key Methods:**
- `generate_prompt(project_data, functionality=None)`: Generates prompt for project
- `apply_template(template, context)`: Applies template to context
- `optimize_prompt(prompt, max_length=None)`: Optimizes prompt length

### MarkdownGenerator

The `MarkdownGenerator` class generates markdown documentation.

```python
from src.generators.markdown_generator import get_markdown_generator

# Create generator
generator = get_markdown_generator()

# Generate markdown
markdown = generator.generate_markdown(project_data, functionalities)
```

**Key Methods:**
- `generate_markdown(project_data, functionalities)`: Generates project documentation
- `create_toc(sections)`: Creates table of contents
- `format_code_samples(samples, language)`: Formats code samples

## AI Integration Classes

### AnthropicIntegration

The `AnthropicIntegration` class integrates with Anthropic Claude.

```python
from src.integrations.anthropic_integration import get_anthropic_integration

# Create integration
integration = get_anthropic_integration()

# Generate analysis
result = integration.analyze_project(project_data, prompt)
```

**Key Methods:**
- `analyze_project(project_data, prompt)`: Analyzes project with Claude
- `generate_suggestions(project_data, functionalities)`: Generates improvement suggestions
- `check_api_key()`: Checks if API key is valid

## Utility Classes

### ConfigManager

The `ConfigManager` class manages configuration.

```python
from src.utils.config_manager import get_config_manager

# Get config manager
config = get_config_manager()

# Get configuration value
api_key = config.get("api_keys.anthropic")

# Set configuration value
config.set("max_file_size_mb", 10)
```

**Key Methods:**
- `get(key, default=None)`: Gets configuration value
- `set(key, value)`: Sets configuration value
- `load_config()`: Loads configuration from file
- `save_config()`: Saves configuration to file

### LogManager

The `LogManager` class manages logging.

```python
from src.utils.logger import get_logger

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

## Command-Line Interface

The main entry point is provided by `src/main.py`, which uses Typer for the CLI.

```bash
# Analyze a project
project-prompt analyze /path/to/project

# Generate prompt for a project
project-prompt generate /path/to/project

# List detected functionalities
project-prompt list /path/to/project

# Generate report for a project
project-prompt report /path/to/project
```

For more details on CLI usage, see the [Script Reference](./script_reference.md).

## Extension Points

Project-Prompt provides several extension points:

1. **Custom Analyzers**: Implement and register in `src/analyzers/`
2. **Custom Templates**: Add to `src/templates/` directory
3. **AI Integrations**: Implement and register in `src/integrations/`
4. **Custom UI**: Extend base UI classes in `src/ui/`

For details on extending Project-Prompt, see the [Development Guide](../development/development_guide.md).
