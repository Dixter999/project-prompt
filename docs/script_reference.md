# ProjectPrompt Script Reference

This document provides detailed information about each script in the ProjectPrompt project, including parameters, functions, and usage examples.

## Main Scripts

### project_prompt.py

The main entry point for ProjectPrompt that provides access to all features through a unified command-line interface.

**Usage:**
```bash
python project_prompt.py COMMAND [OPTIONS]
# or
project-prompt COMMAND [OPTIONS]
```

**Commands:**
- `analyze` - Analyze project structure
- `init` - Initialize a new project
- `docs` - Generate documentation (premium)
- `connections` - Analyze project connectivity (premium)
- `generate-prompts` - Generate contextual prompts

**Functions:**
- `main()` - Entry point that parses arguments and delegates to appropriate scripts
- Delegates analysis to `quick_analyze.py`
- Delegates initialization to `quick_init.py`

**Example:**
```bash
python project_prompt.py analyze ~/my-project
```

### quick_analyze.py

A standalone script for analyzing projects without requiring other parts of the system.

**Usage:**
```bash
python quick_analyze.py [PATH] [OUTPUT_FILE]
```

**Parameters:**
- `PATH` - Path to the project to analyze (default: current directory)
- `OUTPUT_FILE` - Optional JSON file to save the analysis results

**Functions:**
- `analyze_project(path)` - Analyzes a project at the given path
  - Counts files and directories
  - Identifies programming languages
  - Calculates statistics
  - Outputs summary to console
  - Optionally saves to JSON

**Example:**
```bash
python quick_analyze.py ~/my-project analysis.json
```

### project_analyzer.py

A more comprehensive analyzer that provides detailed information about projects.

**Usage:**
```bash
python project_analyzer.py PATH [OUTPUT_FILE]
```

**Parameters:**
- `PATH` - Path to the project to analyze
- `OUTPUT_FILE` - Optional JSON file to save the analysis results

**Functions:**
- `is_binary_file(file_path)` - Checks if a file is binary
- `get_file_language(file_path)` - Detects language by extension
- `analyze_file(file_path)` - Analyzes a single file
- `analyze_project(path, max_files=10000, max_size_mb=5.0)` - Performs detailed analysis
- `detect_important_files(project_data)` - Identifies key project files
- `generate_project_statistics(project_data)` - Creates statistical summary

**Example:**
```bash
python project_analyzer.py ~/my-project detailed_analysis.json
```

### quick_init.py

A script for initializing new projects with a standard structure.

**Usage:**
```bash
python quick_init.py NAME [--path PATH]
```

**Parameters:**
- `NAME` - Name of the new project
- `--path PATH` - Path where to create the project (default: current directory)

**Functions:**
- `init_project(name, path=".")` - Creates a new project structure
- `create_readme(project_path, name)` - Creates README.md
- `create_setup_py(project_path, name)` - Creates setup.py
- `create_gitignore(project_path)` - Creates .gitignore
- `create_basic_src(project_path, name)` - Creates source code structure
- `create_basic_test(project_path, name)` - Creates test structure

**Example:**
```bash
python quick_init.py weather-app --path ~/projects
```

### simple_analyze.py

A simplified project analyzer that provides basic information.

**Usage:**
```bash
python simple_analyze.py [PATH]
```

**Parameters:**
- `PATH` - Path to the project to analyze (default: script directory)

**Functions:**
- `analyze_project(path)` - Performs basic analysis on a project
  - Shows project statistics
  - Displays language distribution
  - Lists important files

**Example:**
```bash
python simple_analyze.py ~/my-project
```

## Utility Scripts

### verify_freemium_system.py

Tests the freemium system implementation to ensure proper restriction of premium features.

**Usage:**
```bash
python verify_freemium_system.py [OPTIONS]
```

**Parameters:**
- `--output, -o FILE` - Path to save results as JSON
- `--set-key, -k KEY` - Set a temporary API key for testing

**Functions:**
- `has_api_key()` - Checks for configured API keys
- `verify_feature_access(feature, api_key_set)` - Verifies access to a feature
- `test_freemium_system()` - Tests all features for proper restrictions

**Example:**
```bash
python verify_freemium_system.py --set-key test_key
```

### set_anthropic_key.py

Sets up API keys for premium features.

**Usage:**
```bash
python set_anthropic_key.py KEY [OPTIONS]
```

**Parameters:**
- `KEY` - The API key to set
- `--config-file FILE` - Path to config file (default: config.yaml)

**Functions:**
- `set_api_key(key, config_file=None)` - Sets and saves the API key

**Example:**
```bash
python set_anthropic_key.py sk_ant_1234567890
```

## Testing Scripts

### test_projectprompt.sh

Basic test script for verifying core functionality.

**Usage:**
```bash
./test_projectprompt.sh
```

**Features:**
- Tests basic analysis
- Tests project structure analysis
- Tests project initialization
- Compares functionality between projects
- Tests standalone analyzers
- Tests with different project parts
- Tests different output formats

**Functions:**
- `run_command()` - Runs a command and logs results
- `print_header()` - Prints section headers

### enhanced_test_projectprompt.sh

Comprehensive test script for all features, including premium features.

**Usage:**
```bash
./enhanced_test_projectprompt.sh
```

**Features:**
All tests from `test_projectprompt.sh`, plus:
- Documentation generation testing
- Connectivity analysis testing
- Freemium system testing
- JSON validation
- Test report generation

**Functions:**
- `run_command()` - Runs a command and logs results
- `print_header()` - Prints section headers
- `validate_json()` - Validates JSON output
- `summarize_results()` - Creates test summary

### run_complete_test.sh

Runs the full test suite and generates a detailed report.

**Usage:**
```bash
./run_complete_test.sh
```

**Features:**
- Runs enhanced tests
- Generates a timestamped report
- Provides summary statistics
- Formats results for easy review

**Functions:**
- Uses `enhanced_test_projectprompt.sh` internally
- Generates report based on template

### cleanup_project.sh

Utility for removing unnecessary files from the project.

**Usage:**
```bash
./cleanup_project.sh [--execute]
```

**Parameters:**
- `--execute` - Actually delete files (without this, it's a dry run)

**Features:**
- Identifies commit scripts
- Finds backup/temp files
- Removes Python cache files
- Cleans other unnecessary files

**Functions:**
- Dry run mode to preview changes
- Selective file deletion

## Source Code Module Structure

The `src/` directory contains the core functionality organized into modules:

### src/analyzers/

- `project_scanner.py` - Scans project structure
- `functionality_detector.py` - Identifies project functionalities
- `file_analyzer.py` - Analyzes individual files
- `functionality_analyzer.py` - Detailed functionality analysis
- `project_progress_tracker.py` - Tracks implementation progress
- `testability_analyzer.py` - Analyzes test coverage

### src/generators/

- `prompt_generator.py` - Basic prompt generation
- `contextual_prompt_generator.py` - Enhanced contextual prompts
- `implementation_prompt_generator.py` - Premium implementation prompts
- `markdown_generator.py` - Documentation generation
- `test_generator.py` - Test case generation

### src/utils/

- `config_manager.py` - Manages configuration
- `telemetry.py` - Anonymous usage tracking
- `project_structure.py` - Project structure utilities
- `license_validator.py` - Validates premium licenses
- `subscription_manager.py` - Manages premium subscriptions
- `api_validator.py` - Validates API credentials
