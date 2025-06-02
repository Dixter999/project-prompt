# -*- coding: utf-8 -*-
"""
Basic implementation templates to replace premium templates.
All features are now available for all users.
"""

IMPLEMENTATION_INSTRUCTION_TEMPLATE = """
# Implementation Guide for {functionality}

## Overview
This guide provides step-by-step instructions for implementing {functionality} in your project.

## Project Context
- Language: {language}
- Framework: {framework}
- Project Type: {project_type}

## Implementation Steps
{implementation_steps}

## Code Examples
{code_examples}

## Best Practices
{best_practices}

## Testing Recommendations
{testing_recommendations}
"""

DESIGN_PATTERNS = {
    "mvc": "Model-View-Controller pattern for separation of concerns",
    "repository": "Repository pattern for data access abstraction",
    "factory": "Factory pattern for object creation",
    "singleton": "Singleton pattern for single instance management",
    "observer": "Observer pattern for event handling"
}

CODE_PATTERNS = {
    "error_handling": "Comprehensive error handling and logging",
    "validation": "Input validation and sanitization",
    "testing": "Unit and integration testing patterns",
    "documentation": "Code documentation and comments"
}

LIBRARY_REFERENCES = {
    "python": ["requests", "pytest", "pydantic", "fastapi"],
    "javascript": ["express", "react", "jest", "axios"],
    "java": ["spring", "junit", "jackson", "lombok"],
    "csharp": ["entity-framework", "xunit", "newtonsoft", "serilog"]
}

ARCHITECTURE_CONSIDERATIONS = """
## Architecture Considerations

1. **Scalability**: Design for future growth
2. **Maintainability**: Write clean, readable code
3. **Security**: Implement proper security measures
4. **Performance**: Optimize for efficiency
5. **Testing**: Ensure comprehensive test coverage
"""

CODE_DOCUMENTATION_TEMPLATES = {
    "function": "Document function purpose, parameters, and return values",
    "class": "Document class responsibilities and usage examples",
    "module": "Document module purpose and main components"
}

SECURITY_CONSIDERATIONS = """
## Security Considerations

1. **Input Validation**: Validate all user inputs
2. **Authentication**: Implement proper user authentication
3. **Authorization**: Control access to resources
4. **Data Protection**: Encrypt sensitive data
5. **Error Handling**: Don't expose sensitive information in errors
"""

PERFORMANCE_CONSIDERATIONS = """
## Performance Considerations

1. **Database Optimization**: Use indexes and optimize queries
2. **Caching**: Implement appropriate caching strategies
3. **Resource Management**: Properly manage memory and connections
4. **Async Operations**: Use asynchronous programming where appropriate
5. **Monitoring**: Implement performance monitoring
"""
