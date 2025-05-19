# Contributing to Project-Prompt

Thank you for considering contributing to Project-Prompt! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others when participating in our community.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/your-username/project-prompt.git
   cd project-prompt
   ```
3. **Set up the development environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

## Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**, following our coding standards.

3. **Write tests** for your changes to ensure they work as expected.

4. **Run the tests** to make sure everything passes:
   ```bash
   pytest
   ```

5. **Commit your changes** with a descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

6. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub from your fork to the main repository.

## Pull Request Guidelines

When submitting a pull request:

1. **Reference any related issues** in the PR description
2. **Describe your changes** clearly and concisely
3. **Include tests** for new functionality
4. **Update documentation** if your changes modify behavior
5. **Make sure all tests pass** before submitting
6. **Keep PRs focused** on a single topic or feature

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding style
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Add type hints to function signatures
- Keep functions focused on a single responsibility

## Testing

- Write unit tests for all new functionality
- Ensure tests are focused and run quickly
- Add integration tests for complex interactions
- Make sure your code has adequate test coverage

## Documentation

- Update documentation when adding or modifying features
- Write clear, concise documentation with examples
- Follow our documentation style guide (Markdown format)
- Check for spelling and grammar errors

## Reporting Issues

When reporting issues, please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Screenshots or code examples if applicable
6. Your environment details (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! When proposing a new feature:

1. Describe the problem you're trying to solve
2. Explain how your proposal solves the problem
3. Provide examples of how the feature would be used
4. Consider edge cases and potential limitations

## Reviewing Pull Requests

We encourage community code reviews. When reviewing PRs:

1. Be respectful and constructive
2. Focus on code quality and correctness
3. Check for adherence to project standards
4. Verify that tests cover the new functionality
5. Ensure documentation is updated

## Getting Help

If you need help with your contribution, you can:

- Open an issue with your question
- Reach out to the maintainers
- Ask in our community channels

Thank you for contributing to Project-Prompt!
