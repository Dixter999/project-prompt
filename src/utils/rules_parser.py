"""
Enhanced Rules Parser for ProjectPrompt

Advanced markdown parsing for structured rules with categories, priorities,
context-specific rules, and template support.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from ..models.rule_models import (
    RuleItem, RuleGroup, RuleSet, RuleContext, RuleTemplate,
    RulePriority, RuleCategory
)

logger = logging.getLogger(__name__)


class RulesParser:
    """Enhanced parser for project rules markdown files"""
    
    def __init__(self):
        """Initialize the parser with pattern matching rules"""
        self.priority_patterns = {
            RulePriority.MANDATORY: [
                r'mandatory', r'required', r'must', r'essential', r'critical'
            ],
            RulePriority.RECOMMENDED: [
                r'recommended', r'preferred', r'should', r'suggested'
            ],
            RulePriority.OPTIONAL: [
                r'optional', r'nice.to.have', r'could', r'consider'
            ]
        }
        
        self.category_patterns = {
            RuleCategory.TECHNOLOGY: [
                r'technology', r'tech', r'framework', r'library', r'stack'
            ],
            RuleCategory.ARCHITECTURE: [
                r'architecture', r'design', r'pattern', r'structure'
            ],
            RuleCategory.CODE_STYLE: [
                r'style', r'format', r'convention', r'coding'
            ],
            RuleCategory.TESTING: [
                r'test', r'testing', r'coverage', r'quality'
            ],
            RuleCategory.DOCUMENTATION: [
                r'documentation', r'docs', r'comment', r'readme'
            ],
            RuleCategory.PERFORMANCE: [
                r'performance', r'optimization', r'speed', r'efficiency'
            ],
            RuleCategory.SECURITY: [
                r'security', r'auth', r'permission', r'access'
            ],
            RuleCategory.DEPLOYMENT: [
                r'deployment', r'deploy', r'build', r'release'
            ]
        }
    
    def parse_rules_file(self, file_path: str) -> RuleSet:
        """
        Parse a rules markdown file into a structured RuleSet
        
        Args:
            file_path: Path to the markdown rules file
            
        Returns:
            Parsed RuleSet object
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return self.parse_rules_content(content, file_path)
        
        except Exception as e:
            logger.error(f"Error parsing rules file {file_path}: {e}")
            return RuleSet(name="empty", description="Failed to parse")
    
    def parse_rules_content(self, content: str, source_file: Optional[str] = None) -> RuleSet:
        """
        Parse rules from markdown content
        
        Args:
            content: Markdown content string
            source_file: Optional source file path for reference
            
        Returns:
            Parsed RuleSet object
        """
        lines = content.split('\n')
        rule_set = RuleSet(
            name=self._extract_project_name(content),
            description=self._extract_project_description(content)
        )
        
        current_category = None
        current_priority = None
        current_group = None
        current_context = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
            
            # Parse headers
            if line.startswith('#'):
                header_level, header_text = self._parse_header(line)
                
                if header_level == 1:
                    # Main title - extract project name if not set
                    if not rule_set.name or rule_set.name == "empty":
                        rule_set.name = header_text.lower().replace(' ', '_')
                
                elif header_level == 2:
                    # Category level
                    current_category = self._identify_category(header_text)
                    current_priority = None
                    current_group = RuleGroup(
                        name=header_text.lower().replace(' ', '_'),
                        category=current_category,
                        description=header_text
                    )
                    rule_set.add_group(current_group)
                
                elif header_level == 3:
                    # Priority or subcategory level
                    priority = self._identify_priority(header_text)
                    if priority:
                        current_priority = priority
                        # Update current group priority if it matches
                        if current_group:
                            current_group.priority = priority
                    else:
                        # This is a subcategory
                        if current_category:
                            subgroup = RuleGroup(
                                name=header_text.lower().replace(' ', '_'),
                                category=current_category,
                                description=header_text
                            )
                            rule_set.add_group(subgroup)
                            current_group = subgroup
            
            # Parse rule items
            elif line.startswith(('-', '*', '+')):
                rule_content = line[1:].strip()
                if rule_content and current_group:
                    # Extract context information from rule content
                    rule_content, extracted_context = self._extract_rule_context(rule_content)
                    
                    # Create rule item
                    rule_item = RuleItem(
                        content=rule_content,
                        priority=current_priority or RulePriority.RECOMMENDED,
                        category=current_category or RuleCategory.CUSTOM,
                        context=extracted_context,
                        source_line=line_num,
                        source_file=source_file
                    )
                    
                    # Extract additional metadata
                    rule_item.tags = self._extract_tags(rule_content)
                    rule_item.examples = self._extract_examples(rule_content)
                    
                    current_group.rules.append(rule_item)
            
            # Parse context blocks
            elif line.startswith('```') and 'context' in line.lower():
                # Start of context block - would need multi-line parsing
                pass
            
            # Parse metadata
            elif ':' in line and not line.startswith('http'):
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['version', 'project_type', 'author']:
                    rule_set.metadata[key] = value
        
        return rule_set
    
    def _parse_header(self, line: str) -> Tuple[int, str]:
        """Parse header line and return level and text"""
        level = len(line) - len(line.lstrip('#'))
        text = line.lstrip('#').strip()
        return level, text
    
    def _identify_category(self, text: str) -> RuleCategory:
        """Identify rule category from text"""
        text_lower = text.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return category
        
        return RuleCategory.CUSTOM
    
    def _identify_priority(self, text: str) -> Optional[RulePriority]:
        """Identify rule priority from text"""
        text_lower = text.lower()
        
        for priority, patterns in self.priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return priority
        
        return None
    
    def _extract_project_name(self, content: str) -> str:
        """Extract project name from content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip().lower().replace(' ', '_')
        return "project_rules"
    
    def _extract_project_description(self, content: str) -> Optional[str]:
        """Extract project description from content"""
        # Look for overview or description section
        lines = content.split('\n')
        in_overview = False
        description_lines = []
        
        for line in lines:
            if line.lower().startswith('## project overview'):
                in_overview = True
                continue
            elif line.startswith('##') and in_overview:
                break
            elif in_overview and line.strip():
                description_lines.append(line.strip())
        
        return ' '.join(description_lines) if description_lines else None
    
    def _extract_rule_context(self, rule_content: str) -> Tuple[str, Optional[RuleContext]]:
        """Extract context information from rule content"""
        context = None
        
        # Look for context patterns in the rule content
        patterns = {
            'directories': r'\[dirs?:\s*([^\]]+)\]',
            'file_patterns': r'\[files?:\s*([^\]]+)\]',
            'file_extensions': r'\[ext:\s*([^\]]+)\]',
            'exclude_patterns': r'\[exclude:\s*([^\]]+)\]',
            'environments': r'\[env:\s*([^\]]+)\]'
        }
        
        context_data = {}
        cleaned_content = rule_content
        
        for key, pattern in patterns.items():
            match = re.search(pattern, rule_content)
            if match:
                values = [v.strip() for v in match.group(1).split(',')]
                context_data[key] = values
                # Remove the context annotation from the content
                cleaned_content = re.sub(pattern, '', cleaned_content).strip()
        
        if context_data:
            context = RuleContext(**context_data)
        
        return cleaned_content, context
    
    def _extract_tags(self, rule_content: str) -> set:
        """Extract tags from rule content"""
        tags = set()
        
        # Look for hashtag-style tags
        tag_pattern = r'#(\w+)'
        matches = re.findall(tag_pattern, rule_content)
        tags.update(matches)
        
        # Look for technology mentions
        tech_pattern = r'\b(react|vue|angular|python|javascript|typescript|java|c\+\+|go|rust|php)\b'
        matches = re.findall(tech_pattern, rule_content.lower())
        tags.update(matches)
        
        return tags
    
    def _extract_examples(self, rule_content: str) -> List[str]:
        """Extract example code or patterns from rule content"""
        examples = []
        
        # Look for inline code examples
        code_pattern = r'`([^`]+)`'
        matches = re.findall(code_pattern, rule_content)
        examples.extend(matches)
        
        return examples
    
    def validate_syntax(self, content: str) -> List[str]:
        """
        Validate rules syntax and structure
        
        Args:
            content: Markdown content to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        lines = content.split('\n')
        
        has_project_header = False
        has_categories = False
        current_category = None
        has_rules = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for project header
            if line.startswith('# '):
                has_project_header = True
            
            # Check for category headers
            elif line.startswith('## '):
                has_categories = True
                current_category = line[3:].strip()
            
            # Check for rule items
            elif line.startswith(('-', '*', '+')):
                has_rules = True
                rule_content = line[1:].strip()
                
                # Validate rule content
                if not rule_content:
                    errors.append(f"Line {line_num}: Empty rule item")
                
                # Check for common formatting issues
                if rule_content.startswith(('use ', 'Use ')) and 'only' in rule_content:
                    # This is a technology constraint - check if it's specific enough
                    if rule_content.count(' ') < 3:
                        errors.append(f"Line {line_num}: Rule might be too vague: '{rule_content}'")
            
            # Check for malformed headers
            elif line.startswith('#'):
                header_level = len(line) - len(line.lstrip('#'))
                if header_level > 4:
                    errors.append(f"Line {line_num}: Header too deep (max 4 levels)")
        
        # Check overall structure
        if not has_project_header:
            errors.append("Missing main project header (# Project Name)")
        
        if not has_categories:
            errors.append("No rule categories found")
        
        if not has_rules:
            errors.append("No rules found")
        
        return errors
    
    def generate_template(self, project_type: str, context: Dict[str, Any]) -> str:
        """
        Generate a rules template for a specific project type
        
        Args:
            project_type: Type of project (web_app, data_science, api_service, etc.)
            context: Context variables for template generation
            
        Returns:
            Generated markdown template content
        """
        if project_type == "web_app":
            return self._generate_web_app_template(context)
        elif project_type == "data_science":
            return self._generate_data_science_template(context)
        elif project_type == "api_service":
            return self._generate_api_service_template(context)
        else:
            return self._generate_generic_template(context)
    
    def _generate_web_app_template(self, context: Dict[str, Any]) -> str:
        """Generate template for web applications"""
        project_name = context.get('project_name', 'My Web App')
        frontend_framework = context.get('frontend_framework', 'React')
        backend_framework = context.get('backend_framework', 'Node.js')
        database = context.get('database', 'PostgreSQL')
        
        return f"""# {project_name} Rules

## Project Overview
{context.get('description', 'A modern web application project')}

## Technology Rules

### Mandatory
- Use {frontend_framework} exclusively for UI components
- Use {backend_framework} for all API development
- Use {database} for data persistence
- Implement proper error handling with try-catch blocks

### Recommended
- Use TypeScript for type safety
- Implement responsive design patterns
- Use modern CSS frameworks for styling

### Optional
- Consider using state management libraries
- Implement PWA features for enhanced user experience

## Architecture Rules

### Mandatory
- Follow component-based architecture
- Separate business logic from UI components
- Implement proper API versioning
- Use environment-specific configurations

### Recommended
- Follow RESTful API design principles
- Implement proper caching strategies
- Use design patterns like MVC or MVP

## Code Style Rules

### Mandatory
- Use consistent naming conventions
- Write self-documenting code with clear variable names
- Implement proper error handling
- Follow framework-specific best practices

### Recommended
- Use ESLint/Prettier for code formatting
- Implement comprehensive logging
- Write meaningful commit messages

## Testing Rules

### Mandatory
- Minimum 80% code coverage for critical components
- Write unit tests for all business logic
- Implement integration tests for API endpoints

### Recommended
- Use end-to-end testing for critical user flows
- Implement performance testing
- Use mocking for external dependencies
"""
    
    def _generate_data_science_template(self, context: Dict[str, Any]) -> str:
        """Generate template for data science projects"""
        project_name = context.get('project_name', 'Data Science Project')
        
        return f"""# {project_name} Rules

## Project Overview
{context.get('description', 'A data science and analytics project')}

## Technology Rules

### Mandatory
- Use pandas for all data manipulation
- Use numpy for numerical computations
- Use {context.get('visualization_lib', 'matplotlib/seaborn')} for data visualization
- Use Jupyter notebooks for exploration and prototyping

### Recommended
- Use scikit-learn for machine learning models
- Use pytest for testing data processing functions
- Use virtual environments for dependency management

## Architecture Rules

### Mandatory
- Separate data processing, analysis, and visualization code
- Use version control for datasets and models
- Implement reproducible data pipelines
- Document data sources and transformations

### Recommended
- Follow clean code principles in analysis scripts
- Use configuration files for parameters
- Implement proper logging for long-running processes

## Documentation Rules

### Mandatory
- Document all data processing steps
- Include data dictionary for datasets
- Write clear methodology documentation
- Document model assumptions and limitations

### Recommended
- Use automated documentation tools
- Include visualizations in documentation
- Maintain a project README with setup instructions
"""
    
    def _generate_api_service_template(self, context: Dict[str, Any]) -> str:
        """Generate template for API services"""
        project_name = context.get('project_name', 'API Service')
        
        return f"""# {project_name} Rules

## Project Overview
{context.get('description', 'A RESTful API service project')}

## Technology Rules

### Mandatory
- Use {context.get('framework', 'FastAPI')} for API development
- Use {context.get('database', 'PostgreSQL')} with ORM
- Implement proper authentication and authorization
- Use OpenAPI/Swagger for API documentation

### Recommended
- Use Redis for caching
- Implement rate limiting
- Use containerization with Docker

## Architecture Rules

### Mandatory
- All services must inherit from BaseService class
- Use dependency injection for external services
- Implement proper error handling with custom exceptions
- Follow RESTful API design principles

### Recommended
- Use repository pattern for data access
- Implement CQRS for complex operations
- Use event-driven architecture for decoupling

## Security Rules

### Mandatory
- Validate all input data
- Implement proper authentication
- Use HTTPS for all communications
- Log security-related events

### Recommended
- Implement API rate limiting
- Use JWT tokens for stateless authentication
- Regular security audits and updates

## Testing Rules

### Mandatory
- Minimum 90% code coverage
- Test all API endpoints
- Mock all external dependencies
- Implement integration tests

### Recommended
- Use contract testing for API consumers
- Implement load testing
- Use automated security testing
"""
    
    def _generate_generic_template(self, context: Dict[str, Any]) -> str:
        """Generate generic template for any project type"""
        project_name = context.get('project_name', 'Project')
        
        return f"""# {project_name} Rules

## Project Overview
{context.get('description', 'Project rules and guidelines')}

## Technology Rules

### Mandatory
- Define your required technologies here
- Specify framework constraints
- List prohibited technologies

### Recommended
- Preferred libraries and tools
- Suggested development practices

## Architecture Rules

### Mandatory
- Core architectural patterns to follow
- Required design principles
- Essential structure guidelines

### Recommended
- Suggested architectural improvements
- Optional design patterns

## Code Style Rules

### Mandatory
- Coding standards to enforce
- Required formatting rules
- Essential naming conventions

### Recommended
- Preferred coding practices
- Suggested style guidelines

## Testing Rules

### Mandatory
- Required testing standards
- Minimum coverage requirements
- Essential test types

### Recommended
- Suggested testing practices
- Optional testing tools
"""