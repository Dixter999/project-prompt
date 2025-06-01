# CLI Tool Project Rules

## Project Overview
This is a command-line interface tool project focused on user experience, cross-platform compatibility, and maintainable code architecture.

## Technology Rules

### Mandatory
- Use Python 3.8+ for all CLI development
- Use Click or argparse for command-line argument parsing
- Use pathlib for all file system operations
- Use rich or colorama for enhanced terminal output and formatting
- Use setuptools or poetry for packaging and distribution

### Recommended
- Use typer for modern CLI development with type hints
- Use pydantic for configuration validation
- Use pytest for comprehensive testing
- Use tox for testing across multiple Python versions
- Use pre-commit hooks for code quality

### Optional
- Consider using textual for terminal user interfaces
- Consider using shellingham for shell detection
- Use questionary for interactive prompts

## Architecture Rules

### Mandatory
- Separate CLI interface from business logic (commands vs core functionality)
- Implement proper error handling with user-friendly messages
- Use configuration files for user preferences and settings
- All commands must have help text and examples
- Implement proper exit codes for different scenarios

### Recommended
- Follow command pattern for CLI command organization
- Implement plugin architecture for extensibility
- Use dependency injection for testability
- Implement proper logging with different verbosity levels

### Optional
- Consider implementing shell completion for better UX
- Use configuration inheritance (global, local, environment)

## Code Style Rules

### Mandatory
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return types
- Maximum function length: 50 lines
- All public functions must have docstrings
- Use meaningful command and option names

### Recommended
- Use black for automatic code formatting
- Use isort for import organization
- Follow single responsibility principle for commands
- Use descriptive variable names throughout

### Optional
- Consider using pylint for additional code quality checks
- Implement docstring validation with pydocstyle

## Testing Rules

### Mandatory
- Minimum 85% code coverage for all business logic
- All CLI commands must have integration tests
- Test both success and failure scenarios
- Mock all external dependencies (file system, network, etc.)
- Use pytest's click testing utilities for CLI testing

### Recommended
- Test CLI output and error messages
- Implement property-based testing for input validation
- Test cross-platform compatibility
- Use golden master testing for complex output formatting

### Optional
- Consider end-to-end testing with real command execution
- Implement performance testing for large dataset processing

## Performance Rules

### Mandatory
- CLI startup time must be under 1 second
- Implement progress bars for long-running operations
- Use streaming for large file processing
- Implement efficient algorithms for data processing

### Recommended
- Use lazy loading for heavy imports
- Implement caching for expensive operations
- Use parallel processing where appropriate
- Optimize memory usage for large datasets

### Optional
- Consider using compiled extensions for performance-critical code
- Implement incremental processing for very large datasets

## Usability Rules

### Mandatory
- Provide clear, actionable error messages
- Implement consistent command structure and naming
- Include comprehensive help text for all commands and options
- Support common output formats (JSON, CSV, table)

### Recommended
- Implement interactive mode for complex operations
- Use colors and formatting to improve readability
- Provide examples in help text
- Implement configuration file support

### Optional
- Consider implementing shell integration and completion
- Provide verbose and quiet modes for different use cases

## Documentation Rules

### Mandatory
- Include comprehensive README with installation and usage examples
- Document all command-line options and arguments
- Include troubleshooting section for common issues
- Provide man pages for Unix-like systems

### Recommended
- Use automated documentation generation from docstrings
- Include video demonstrations for complex features
- Document configuration file format and options
- Provide migration guides for version updates

### Optional
- Consider creating interactive tutorials
- Implement built-in documentation browser

## Deployment Rules

### Mandatory
- Support installation via pip/PyPI
- Include proper dependency management
- Support multiple Python versions (3.8+)
- Include proper versioning and release management

### Recommended
- Provide binary distributions for major platforms
- Use CI/CD for automated testing and releases
- Include homebrew formula for macOS users
- Implement automatic update checking

### Optional
- Consider packaging as standalone executables
- Provide Docker images for containerized usage

## Cross-Platform Rules

### Mandatory
- Test on Windows, macOS, and Linux
- Use os.path or pathlib for path handling
- Handle different line endings properly
- Use appropriate default configurations per platform

### Recommended
- Implement platform-specific features where beneficial
- Use environment variables following platform conventions
- Handle Unicode and encoding properly
- Test with different terminal emulators

### Optional
- Consider platform-specific packaging (MSI, DMG, DEB)
- Implement platform-specific integrations

## AI Analysis Preferences

### Focus Areas
1. CLI usability and user experience design
2. Error handling and user-friendly messaging
3. Cross-platform compatibility issues
4. Performance optimization for CLI responsiveness
5. Code organization and maintainability

### Suggestion Priorities
1. User experience improvements (error messages, help text)
2. Cross-platform compatibility issues
3. Performance bottlenecks affecting CLI responsiveness
4. Code maintainability and architecture
5. Testing coverage for CLI scenarios
6. Documentation completeness

## Custom Analysis Rules

### When analyzing this project:
1. Always check CLI command structure and consistency
2. Verify error handling provides actionable user feedback
3. Ensure proper use of exit codes and status messages
4. Check for cross-platform compatibility issues
5. Validate help text and documentation completeness

### When suggesting improvements:
1. Prioritize user experience and usability improvements
2. Suggest CLI-specific patterns and conventions
3. Recommend cross-platform solutions
4. Focus on performance and responsiveness
5. Ensure suggestions follow CLI design best practices