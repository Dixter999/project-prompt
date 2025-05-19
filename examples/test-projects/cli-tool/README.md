# CLI Tool Test Template

This project demonstrates a command-line interface tool structure for testing Anthropic's markdown generation capabilities.

## Features

- Multiple commands with subparsers
- Configuration file support
- Modular command implementation
- Logging system
- Input/output formatting options

## Usage

```bash
# Initialize a new project
python cli.py init /path/to/new/project --template basic

# Analyze a project or file
python cli.py analyze /path/to/target --output analysis.md --format markdown

# Generate output from template
python cli.py generate template_name --output /output/dir --vars variables.json

# Validate a file or configuration
python cli.py validate config.yaml --schema schema.json
```

## Structure

- `cli.py` - Main entry point with command parsing
- `src/commands/` - Command implementation modules
- `src/utils/` - Utility functions and helpers
- `tests/` - Unit and integration tests

## Configuration

Create a `config.yaml` file with your settings:

```yaml
# Example configuration
output_dir: ./output
templates_dir: ./templates
log_level: info
default_format: markdown
```

Then use it with any command:

```bash
python cli.py -c config.yaml analyze /path/to/project
```
