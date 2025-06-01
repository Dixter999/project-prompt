# API Service Project Rules

## Project Overview
This is a RESTful API service project focused on scalable backend architecture, security, and reliable data processing.

## Technology Rules

### Mandatory
- Use FastAPI exclusively for API development [files: *.py, dirs: api/]
- Use PostgreSQL with SQLAlchemy ORM for all database operations
- Use Pydantic for request/response validation and serialization
- Use Python 3.8+ with type hints throughout the codebase
- Use JWT tokens for authentication

### Recommended
- Use Redis for caching and session management
- Use Celery for background task processing
- Use pytest for comprehensive testing
- Use Alembic for database migrations
- Use uvicorn for ASGI server in production

### Optional
- Consider using Docker for containerization
- Consider implementing GraphQL with Strawberry
- Use Elasticsearch for advanced search capabilities

## Architecture Rules

### Mandatory
- All services must inherit from BaseService class
- Use dependency injection for external services and database connections
- Implement proper separation of concerns (controllers, services, repositories)
- All API endpoints must follow RESTful conventions
- Use structured logging with correlation IDs

### Recommended
- Follow repository pattern for data access layer
- Implement CQRS pattern for complex business operations
- Use event-driven architecture for loose coupling
- Implement proper middleware for cross-cutting concerns

### Optional
- Consider microservices architecture for large applications
- Implement API gateway pattern for service orchestration

## Code Style Rules

### Mandatory
- Follow PEP 8 style guidelines strictly
- Use type hints for all function parameters and return types
- Maximum function length: 50 lines
- Maximum class length: 200 lines
- All public methods must have comprehensive docstrings

### Recommended
- Use black for automatic code formatting
- Use isort for import organization
- Follow single responsibility principle for classes and functions
- Use meaningful names for variables, functions, and classes

### Optional
- Consider using pylint for additional code quality checks
- Implement code complexity analysis with radon

## Testing Rules

### Mandatory
- Minimum 90% code coverage for all business logic
- All API endpoints must have integration tests
- All database operations must be tested with transactions and rollback
- Mock all external API calls and third-party services
- Use pytest fixtures for common test data and setup

### Recommended
- Implement contract testing for API consumers
- Use factory pattern for test data generation
- Implement load testing with locust or similar tools
- Use property-based testing for data validation

### Optional
- Consider mutation testing for test quality assessment
- Implement chaos engineering tests for resilience

## Performance Rules

### Mandatory
- All API endpoints must respond within 500ms for 95% of requests
- Implement proper database indexing for frequently queried fields
- Use connection pooling for database connections
- Implement request/response caching where appropriate

### Recommended
- Use async/await for I/O-bound operations
- Implement database query optimization and monitoring
- Use CDN for static content delivery
- Implement proper pagination for large datasets

### Optional
- Consider implementing database read replicas for scaling
- Use message queues for async processing

## Security Rules

### Mandatory
- All inputs must be validated and sanitized using Pydantic
- Implement proper authentication and authorization
- Use parameterized queries to prevent SQL injection
- Store sensitive data encrypted at rest and in transit
- Implement proper CORS configuration

### Recommended
- Use rate limiting to prevent abuse
- Implement API key management for external integrations
- Regular security audits and dependency scanning
- Use HTTPS everywhere with proper certificate management

### Optional
- Consider implementing OAuth 2.0 / OpenID Connect
- Implement API versioning for backward compatibility

## Documentation Rules

### Mandatory
- All API endpoints must have OpenAPI/Swagger documentation
- Include request/response examples for all endpoints
- Document all configuration options and environment variables
- Maintain API changelog for version tracking

### Recommended
- Use automated documentation generation with FastAPI
- Include error response documentation with proper status codes
- Document deployment and scaling procedures
- Implement interactive API documentation

### Optional
- Consider creating SDK/client libraries for API consumers
- Implement API usage analytics and monitoring

## Deployment Rules

### Mandatory
- Use containerization (Docker) for consistent deployments
- Implement proper CI/CD pipeline with automated testing
- Use environment variables for all configuration
- Implement proper database backup and recovery procedures

### Recommended
- Use infrastructure as code (Terraform, Ansible)
- Implement blue-green or rolling deployment strategies
- Use monitoring and alerting (Prometheus, Grafana)
- Implement centralized logging with ELK stack

### Optional
- Consider using Kubernetes for container orchestration
- Implement service mesh for advanced traffic management

## AI Analysis Preferences

### Focus Areas
1. API security vulnerabilities and best practices
2. Database query optimization and N+1 problems
3. FastAPI-specific performance optimizations
4. Proper error handling and status code usage
5. Authentication and authorization implementation

### Suggestion Priorities
1. Security vulnerabilities (highest priority)
2. Performance bottlenecks and database issues
3. API design and RESTful principles
4. Error handling and logging improvements
5. Code maintainability and architecture
6. Testing coverage and quality

## Custom Analysis Rules

### When analyzing this project:
1. Always check for proper input validation with Pydantic
2. Verify database operations use ORM and proper transactions
3. Ensure API endpoints follow RESTful conventions and status codes
4. Check for proper error handling and logging throughout
5. Validate authentication and authorization implementation

### When suggesting improvements:
1. Prioritize security fixes over performance optimizations
2. Suggest FastAPI-specific solutions and patterns
3. Recommend proper HTTP status codes and error responses
4. Focus on scalability and maintainability
5. Ensure suggestions follow API design best practices