# Project Rules and Context

## Project Overview
This is a financial data analysis platform built with Python, focusing on real-time market data processing and visualization.

## Technology Constraints

### Mandatory Technologies
- **UI Framework**: Use Streamlit exclusively for all user interfaces
- **Data Processing**: pandas for all data manipulation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Framework**: FastAPI for all REST endpoints
- **Testing**: pytest with minimum 80% coverage

### Prohibited Technologies
- Do NOT use Flask or Django
- Avoid matplotlib, use plotly for all visualizations
- No raw SQL queries, always use ORM

## Architecture Rules

### Service Structure
- All service classes MUST inherit from `BaseService`
- Services must follow dependency injection pattern
- Each service should have a corresponding interface

### File Organization
```
src/
  ├── models/       # Database models only
  ├── services/     # Business logic
  ├── api/          # FastAPI endpoints
  ├── ui/           # Streamlit pages
  ├── utils/        # Helper functions
  └── config/       # Configuration files
```

### Naming Conventions
- Services: `*Service` (e.g., `UserService`, `DataService`)
- Models: Singular nouns (e.g., `User`, `Transaction`)
- API endpoints: RESTful conventions (`/api/v1/users`)
- Streamlit pages: `page_*.py`

## Code Style Requirements

### Python Specific
- Type hints required for all function parameters and returns
- Docstrings mandatory for all public methods
- Maximum function length: 50 lines
- Maximum file length: 500 lines

### Error Handling
- All exceptions must be logged with context
- Use custom exceptions inheriting from `BaseException`
- Never use bare `except:` clauses

## Testing Requirements

### Unit Tests
- Minimum 80% code coverage
- Test files must mirror source structure
- Use fixtures for common test data
- Mock all external dependencies

### Integration Tests
- Required for all API endpoints
- Database tests must use transactions and rollback

## AI Analysis Preferences

### Focus Areas
1. Performance optimization in data processing
2. Security vulnerabilities in API endpoints
3. Streamlit-specific best practices
4. Database query optimization

### Suggestion Priorities
1. Code that violates mandatory rules
2. Performance bottlenecks
3. Security issues
4. Code duplication
5. Missing tests

## Documentation Standards

### Code Documentation
- All public functions must have docstrings
- Complex algorithms need inline comments
- README required for each major module

### API Documentation
- OpenAPI/Swagger for all endpoints
- Request/response examples required
- Error responses must be documented

## Custom Analysis Rules

### When analyzing this project:
1. Always check Streamlit compatibility first
2. Prioritize performance for data processing functions
3. Ensure all database operations use ORM
4. Verify dependency injection is properly implemented
5. Check that all services have corresponding tests

### When suggesting improvements:
1. Only suggest Streamlit-compatible UI solutions
2. Prefer pandas operations over pure Python loops
3. Suggest caching strategies for expensive operations
4. Recommend async patterns where applicable
5. Focus on maintainability over premature optimization
