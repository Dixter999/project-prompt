# Library Project Template

A Python library template for testing Anthropic's markdown generation capabilities.

## Features

- Organized package structure
- Documentation with Sphinx
- Unit tests with pytest
- Type annotations
- Example usage scripts
- Developer tooling configuration

## Installation

```bash
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

```python
from testlib import Calculator

# Create an instance
calc = Calculator()

# Perform operations
result = calc.add(5, 3)
print(f"Result: {result}")  # Output: Result: 8
```

## Project Structure

- `src/`: Source code package
- `tests/`: Unit and integration tests
- `docs/`: Documentation
- `examples/`: Example usage scripts

## Development

Setup development environment:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build documentation
cd docs
make html
```
