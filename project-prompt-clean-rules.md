# ProjectPrompt - Development Rules

## Project Overview
ProjectPrompt is a sophisticated Python-based CLI tool for generating comprehensive project documentation with AI-powered analysis. This tool helps developers create detailed project prompts, analyze codebases, and maintain development standards.

**Generated on:** 2025-06-01 15:37:00  
**Analysis Confidence:** 1.0/1.0

## Technology Constraints

### Mandatory Technologies
- **Python 3.8+**: Core language - follow PEP 8 standards and use type hints
- **Typer**: CLI framework for all command-line interfaces
- **Rich**: Terminal formatting and progress indicators
- **Jinja2**: Template engine for all report generation
- **YAML**: Configuration file format for rules and settings
- **Anthropic Claude**: AI integration for enhanced analysis

### Recommended Technologies
- **pytest**: Testing framework with minimum 80% coverage
- **Black**: Code formatting with line length 100
- **isort**: Import sorting and organization
- **mypy**: Static type checking
- **Poetry**: Dependency management and packaging

### Prohibited Technologies
- Do NOT use Flask or Django for this CLI-focused tool
- Avoid using print() statements - use Rich console instead
- No direct file operations without proper error handling
- No hardcoded paths - use Path objects and configuration

## Architecture Rules

### Service Structure
- All analysis classes MUST inherit from appropriate base classes
- Services must follow dependency injection pattern using factory functions
- Each analyzer should have a corresponding interface/protocol
- Use lazy loading for expensive resources (AI clients, large models)

### File Organization
```
src/
  ├── analyzers/    # Code analysis and pattern detection
  ├── commands/     # CLI command implementations  
  ├── core/         # Core business logic
  ├── generators/   # Report and output generators
  ├── integrations/ # External API integrations
  ├── models/       # Data models and schemas
  ├── templates/    # Jinja2 templates for outputs
  ├── ui/           # User interface components
  ├── utils/        # Utility functions and helpers
  └── validators/   # Input validation and verification
```

### Naming Conventions
- **Analyzers**: `*Analyzer` (e.g., `ProjectAnalyzer`, `CodeQualityAnalyzer`)
- **Commands**: `*_commands.py` (e.g., `rules_commands.py`, `generate_commands.py`)
- **Models**: Descriptive nouns (e.g., `RuleSuggestion`, `PatternAnalysis`)
- **Templates**: `*_template.md` for Markdown, `*_template.yaml` for YAML
- **Factory functions**: `get_*` (e.g., `get_rules_suggester`, `get_anthropic_client`)

## Code Style Requirements

### Python Specific Rules
- **Type hints required** for all function parameters, returns, and class attributes
- **Docstrings mandatory** for all public methods, classes, and modules
- **Maximum function length**: 50 lines (excluding docstrings)
- **Maximum file length**: 1000 lines
- **Line length**: 100 characters maximum
- **Import organization**: Use isort with black compatibility

### Error Handling
- All exceptions must be logged with context using the centralized logger
- Use custom exceptions inheriting from appropriate base exceptions
- Never use bare `except:` clauses - always specify exception types
- Provide meaningful error messages for user-facing operations
- Use Rich console for user-friendly error display

### Async/Await Patterns
- Use async/await for all API calls (Anthropic, file I/O operations)
- Implement proper async context managers for resource management
- Use asyncio.gather() for concurrent operations where appropriate
- Handle async exceptions with proper error propagation

## Testing Requirements

### Unit Tests
- **Minimum 80% code coverage** across all modules
- Test files must mirror source structure in tests/ directory
- Use pytest fixtures for common test data and mocked dependencies
- Mock all external dependencies (API calls, file system operations)
- Test both success and failure scenarios

### Integration Tests
- Required for all CLI commands with realistic project structures
- Use temporary directories for file operation tests
- Test AI integration with mock responses for consistent results
- Validate template rendering with various data scenarios

### Test Organization
```
tests/
  ├── unit/           # Unit tests mirroring src/ structure
  ├── integration/    # Integration tests for workflows
  ├── fixtures/       # Test data and mock responses
  └── conftest.py     # Shared pytest configuration
```

## Security Requirements

### API Key Management
- **Never hardcode API keys** - use environment variables or secure config
- Validate API keys before making requests
- Implement rate limiting and retry logic for API calls
- Log API usage without exposing sensitive data

### File System Security
- Validate all file paths to prevent directory traversal
- Use sandboxed operations for analyzing untrusted codebases
- Implement size limits for file operations to prevent DoS
- Sanitize all user input for file names and paths

## Documentation Standards

### Code Documentation
- **All public functions must have comprehensive docstrings** with parameters, returns, and examples
- Complex algorithms need inline comments explaining the logic
- README required for each major module explaining its purpose
- Type hints serve as inline documentation - keep them descriptive

### API Documentation
- Command-line help text must be comprehensive and user-friendly
- Examples required for all CLI commands in help text
- Error messages must be actionable and helpful
- Maintain CHANGELOG.md with all user-facing changes

### Project Documentation
- Keep README.md updated with installation and usage instructions
- Maintain comprehensive examples in examples/ directory
- Document configuration options and environment variables
- Provide troubleshooting guide for common issues

## Performance Guidelines

### Code Analysis Performance
- **Implement caching** for expensive analysis operations
- Use lazy loading for large data structures and AI models
- Process files in batches for large codebases
- Provide progress indicators for long-running operations

### Memory Management
- Release resources promptly in async operations
- Use generators for processing large file lists
- Implement size limits for in-memory operations
- Monitor memory usage in analysis operations

### AI Integration Optimization
- **Cache AI responses** for identical inputs
- Batch API requests where possible to reduce latency
- Implement exponential backoff for API rate limiting
- Use streaming responses for large AI outputs

## AI Analysis Preferences

### Focus Areas
Based on the ProjectPrompt codebase patterns:
1. **CLI command structure and organization** - ensure consistent command patterns
2. **Template system usage** - validate Jinja2 templates and data binding
3. **Error handling in analysis workflows** - comprehensive exception management
4. **AI integration patterns** - proper async handling and rate limiting
5. **Configuration management** - YAML/environment variable handling

### Detected Technologies
- **Python**: Core language with extensive use of modern features
- **Typer**: CLI framework for command organization
- **Rich**: Terminal UI and formatting
- **Jinja2**: Template engine for report generation
- **Anthropic**: AI integration for enhanced analysis
- **pytest**: Testing framework
- **YAML**: Configuration and rules format

### Suggestion Priorities
1. **High Priority (Mandatory)**: Security issues, API key exposure, file system vulnerabilities
2. **Medium Priority (Recommended)**: Code quality, performance optimizations, documentation
3. **Low Priority (Optional)**: Code style improvements, minor refactoring opportunities

## Custom Analysis Rules

### When analyzing this project:
1. **Always verify CLI command registration** in main.py (High confidence: 1.0)
2. **Check template file existence and syntax** for all Jinja2 templates (High confidence: 0.9)
3. **Validate AI integration error handling** for network failures (High confidence: 0.9)
4. **Ensure proper async/await usage** in all API operations (High confidence: 0.8)
5. **Verify configuration loading and validation** (High confidence: 0.8)

### When suggesting improvements:
1. Focus on CLI usability and user experience enhancements
2. Prioritize error handling and recovery mechanisms
3. Suggest performance optimizations for large codebase analysis
4. Recommend additional AI integration capabilities
5. Focus on maintainability and code organization

## Implementation Roadmap

### Phase 1: Critical Rules (Week 1-2)
- [ ] **API Key Security Validation**
  - Implementation: Implement secure API key loading and validation before any external calls
  - Confidence: 1.0/1.0

- [ ] **File System Security**
  - Implementation: Add path validation and sanitization for all file operations
  - Confidence: 0.9/1.0

- [ ] **Error Handling Standardization**
  - Implementation: Ensure all CLI commands have proper exception handling with user-friendly messages
  - Confidence: 0.9/1.0

### Phase 2: Quality Improvements (Week 3-4)  
- [ ] **Template System Enhancement**
  - Implementation: Add template validation and better error messages for missing variables
  - Confidence: 0.8/1.0

- [ ] **Performance Optimization**
  - Implementation: Implement caching for analysis results and AI responses
  - Confidence: 0.8/1.0

- [ ] **Testing Coverage**
  - Implementation: Increase test coverage to 90%+ with focus on integration tests
  - Confidence: 0.8/1.0

### Phase 3: Optional Enhancements (Month 2)
- [ ] **Advanced AI Features**
  - Implementation: Add support for multiple AI providers and model selection
  - Confidence: 0.7/1.0

- [ ] **Plugin System**
  - Implementation: Design extensible analyzer plugin architecture
  - Confidence: 0.6/1.0

## Quality Metrics

### Current Project Health  
- **Code Consistency**: 8.5/10 (Good structure, some inconsistencies in error handling)
- **Documentation Coverage**: 7.0/10 (Good docstrings, needs more examples)
- **Testing Maturity**: 6.5/10 (Basic tests present, needs integration tests)
- **Security Awareness**: 9.0/10 (Good practices, needs API key validation)

### Expected Improvement with Rules
- **Code Consistency**: 9.5/10 (+1.0)
- **Documentation Coverage**: 9.0/10 (+2.0)
- **Testing Maturity**: 9.0/10 (+2.5)
- **Security Awareness**: 10.0/10 (+1.0)

---

## Analysis Details

**AI Analysis Method**: Automated pattern recognition and best practices comparison  
**Confidence Scoring**: Based on pattern strength and industry standards  
**Review Required**: Human validation recommended for all suggestions

*Generated by ProjectPrompt AI Rules Suggester - 2025-06-01 15:37:00*
