# Web Application Project Rules

## Project Overview
This is a modern web application project focusing on responsive design, user experience, and maintainable code architecture.

## Technology Rules

### Mandatory
- Use React exclusively for UI components [files: *.jsx, *.tsx]
- Use Node.js with Express for backend API development
- Use PostgreSQL for all database operations
- Implement TypeScript for type safety across the entire codebase
- Use HTTPS for all production communications

### Recommended
- Prefer Next.js for React applications with SSR requirements
- Use Redux Toolkit for complex state management
- Use Tailwind CSS or styled-components for styling
- Use Jest and React Testing Library for testing
- Use ESLint and Prettier for code formatting

### Optional
- Consider using Storybook for component documentation
- Consider implementing PWA features
- Use Cypress for end-to-end testing

## Architecture Rules

### Mandatory
- Follow component-based architecture with clear separation of concerns
- All API routes must be versioned (e.g., /api/v1/users)
- Implement proper error boundaries in React components
- Use environment-specific configuration files
- All components must be functional components with hooks

### Recommended
- Follow atomic design principles for component organization
- Implement proper caching strategies (Redis for sessions, browser cache for static assets)
- Use repository pattern for data access layer
- Implement proper logging with structured log format

### Optional
- Consider microservices architecture for large applications
- Implement event-driven architecture for real-time features

## Code Style Rules

### Mandatory
- Use consistent naming conventions: PascalCase for components, camelCase for functions/variables
- All functions must have proper TypeScript type annotations
- Maximum function length: 50 lines
- Maximum file length: 300 lines
- No console.log statements in production code

### Recommended
- Use meaningful variable and function names (avoid abbreviations)
- Implement comprehensive JSDoc comments for public APIs
- Follow BEM methodology for CSS class naming
- Use async/await instead of Promise chains

### Optional
- Consider using functional programming principles where appropriate
- Implement code splitting for better performance

## Testing Rules

### Mandatory
- Minimum 80% code coverage for all business logic
- All API endpoints must have integration tests
- All React components must have unit tests
- Mock all external API calls in tests
- Tests must pass before any code merge

### Recommended
- Use test-driven development (TDD) for critical features
- Implement visual regression testing for UI components
- Use factories/builders for test data generation
- Implement performance testing for critical user flows

### Optional
- Consider mutation testing for test quality assessment
- Implement contract testing for API integrations

## Performance Rules

### Mandatory
- All pages must load within 3 seconds on 3G network
- Images must be optimized and use appropriate formats (WebP when supported)
- Implement lazy loading for non-critical components
- Bundle size must not exceed 2MB for initial load

### Recommended
- Use React.memo and useMemo for expensive computations
- Implement code splitting at route level
- Use CDN for static asset delivery
- Implement proper caching headers

### Optional
- Consider using service workers for offline functionality
- Implement resource hints (preload, prefetch) for critical resources

## Security Rules

### Mandatory
- All user inputs must be validated and sanitized
- Implement proper authentication and authorization
- Use parameterized queries to prevent SQL injection
- Store sensitive data (passwords, tokens) securely (hashed/encrypted)
- Implement proper CORS configuration

### Recommended
- Use Content Security Policy (CSP) headers
- Implement rate limiting on API endpoints
- Regular security audits and dependency updates
- Use HTTPS everywhere (including development)

### Optional
- Consider implementing OAuth 2.0 / OpenID Connect
- Implement security headers (HSTS, X-Frame-Options, etc.)

## Documentation Rules

### Mandatory
- All public APIs must have OpenAPI/Swagger documentation
- Each component must have usage examples
- README must include setup and deployment instructions
- All configuration options must be documented

### Recommended
- Use automated documentation generation tools
- Maintain a changelog for version tracking
- Document architecture decisions in ADRs
- Include troubleshooting guides

### Optional
- Consider creating video tutorials for complex features
- Implement interactive API documentation

## Deployment Rules

### Mandatory
- Use containerization (Docker) for consistent environments
- Implement proper CI/CD pipeline with automated testing
- Use environment variables for configuration
- Implement proper backup strategies for databases

### Recommended
- Use infrastructure as code (Terraform, CloudFormation)
- Implement blue-green deployment strategy
- Use monitoring and alerting (error tracking, performance monitoring)
- Implement automated security scanning in CI/CD

### Optional
- Consider using Kubernetes for orchestration
- Implement canary deployments for critical releases

## AI Analysis Preferences

### Focus Areas
1. React component optimization and best practices
2. TypeScript type safety and proper usage
3. API security and performance
4. Bundle size optimization
5. Accessibility compliance (WCAG guidelines)

### Suggestion Priorities
1. Security vulnerabilities (highest priority)
2. Performance bottlenecks
3. Code maintainability issues
4. React/TypeScript best practices
5. UI/UX improvements
6. Testing coverage gaps

## Custom Analysis Rules

### When analyzing this project:
1. Always check React component patterns and hooks usage
2. Verify TypeScript types are properly defined and used
3. Ensure API endpoints follow RESTful conventions
4. Check for proper error handling in both frontend and backend
5. Validate accessibility standards compliance

### When suggesting improvements:
1. Prioritize security fixes over performance optimizations
2. Suggest React-specific solutions and patterns
3. Recommend TypeScript improvements for better type safety
4. Focus on user experience and performance
5. Ensure suggestions align with modern web development practices