"""
Enhanced Rules Manager for ProjectPrompt

Advanced rules management with categories, priorities, templates, and context-specific rules.
Integrates with the new rule models and enhanced parser for comprehensive rule handling.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import json
import time

from ..models.rule_models import (
    RuleSet, RuleGroup, RuleItem, RuleTemplate, RuleContext,
    RulePriority, RuleCategory,
    get_web_app_template, get_data_science_template, get_api_service_template
)
from .rules_parser import RulesParser

logger = logging.getLogger(__name__)


class EnhancedRulesManager:
    """
    Enhanced manager for project rules with advanced features:
    - Category-based rule organization
    - Priority levels (mandatory/recommended/optional)
    - Context-specific rules
    - Rule templates for different project types
    - Rule inheritance and composition
    - Validation and compliance checking
    """
    
    DEFAULT_RULES_FILENAME = "project-prompt-rules.md"
    CACHE_EXPIRATION = 300  # 5 minutes
    
    def __init__(self, project_root: str = None):
        """
        Initialize the enhanced rules manager
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or os.getcwd()
        self.parser = RulesParser()
        self.rule_set: Optional[RuleSet] = None
        self.templates: Dict[str, RuleTemplate] = {}
        self.last_loaded = 0
        self.rules_file_path: Optional[str] = None
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Try to load rules automatically
        self.load_rules()
    
    def _load_builtin_templates(self):
        """Load built-in rule templates"""
        self.templates.update({
            'web_app': get_web_app_template(),
            'data_science': get_data_science_template(),
            'api_service': get_api_service_template()
        })
    
    def find_rules_file(self) -> Optional[str]:
        """
        Find rules file in project directories
        
        Returns:
            Path to rules file if found, None otherwise
        """
        possible_locations = [
            os.path.join(self.project_root, self.DEFAULT_RULES_FILENAME),
            os.path.join(self.project_root, "project-output", self.DEFAULT_RULES_FILENAME),
            os.path.join(self.project_root, ".projectprompt", self.DEFAULT_RULES_FILENAME),
            os.path.join(self.project_root, "docs", self.DEFAULT_RULES_FILENAME),
        ]
        
        for location in possible_locations:
            if os.path.isfile(location):
                logger.info(f"Found rules file at: {location}")
                return location
        
        logger.info("No rules file found in project")
        return None
    
    def load_rules(self, force_reload: bool = False) -> bool:
        """
        Load and parse rules from file
        
        Args:
            force_reload: Force reload even if cache is valid
            
        Returns:
            True if rules were loaded successfully
        """
        # Find rules file
        if not self.rules_file_path:
            self.rules_file_path = self.find_rules_file()
            if not self.rules_file_path:
                logger.info("No rules file found, creating empty rule set")
                self.rule_set = RuleSet(name="empty_project", description="No rules defined")
                return False
        
        # Check cache validity
        current_time = time.time()
        file_mtime = os.path.getmtime(self.rules_file_path)
        
        if (not force_reload and 
            self.last_loaded > 0 and
            current_time - self.last_loaded < self.CACHE_EXPIRATION and
            file_mtime < self.last_loaded):
            return True
        
        try:
            # Parse rules file
            self.rule_set = self.parser.parse_rules_file(self.rules_file_path)
            self.last_loaded = current_time
            
            logger.info(f"Loaded {len(self.rule_set.groups)} rule groups from {self.rules_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self.rule_set = RuleSet(name="error", description="Failed to load rules")
            return False
    
    def get_all_rules(self) -> List[RuleItem]:
        """
        Get all rules from all groups
        
        Returns:
            List of all rules
        """
        if not self.rule_set:
            return []
        
        all_rules = []
        for group in self.rule_set.groups.values():
            all_rules.extend(group.rules)
        return all_rules
    
    def get_rules_by_category(self, category: RuleCategory) -> List[RuleItem]:
        """
        Get all rules for a specific category
        
        Args:
            category: Rule category to filter by
            
        Returns:
            List of rules in the category
        """
        if not self.rule_set:
            return []
        
        return self.rule_set.get_rules_by_category(category)
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[RuleItem]:
        """
        Get all rules with specific priority
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of rules with the priority
        """
        if not self.rule_set:
            return []
        
        return self.rule_set.get_rules_by_priority(priority)
    
    def get_mandatory_rules(self) -> List[RuleItem]:
        """Get all mandatory rules"""
        return self.get_rules_by_priority(RulePriority.MANDATORY)
    
    def get_applicable_rules(self, file_path: str) -> List[RuleItem]:
        """
        Get rules that apply to a specific file
        
        Args:
            file_path: Path to check rules against
            
        Returns:
            List of applicable rules
        """
        if not self.rule_set:
            return []
        
        return self.rule_set.get_applicable_rules(file_path)
    
    def get_technology_constraints(self) -> Dict[str, List[RuleItem]]:
        """
        Get technology constraints organized by priority
        
        Returns:
            Dictionary mapping priority to technology rules
        """
        tech_rules = self.get_rules_by_category(RuleCategory.TECHNOLOGY)
        
        constraints = {
            'mandatory': [],
            'recommended': [],
            'optional': [],
            'prohibited': []
        }
        
        for rule in tech_rules:
            priority_key = rule.priority.value if rule.priority else 'optional'
            
            # Check if it's a prohibition rule
            if any(word in rule.content.lower() for word in ['never', 'not', 'avoid', 'prohibited']):
                constraints['prohibited'].append(rule)
            else:
                constraints[priority_key].append(rule)
        
        return constraints
    
    def get_architecture_patterns(self) -> List[RuleItem]:
        """Get architecture and design pattern rules"""
        return self.get_rules_by_category(RuleCategory.ARCHITECTURE)
    
    def get_code_style_rules(self) -> List[RuleItem]:
        """Get code style and formatting rules"""
        return self.get_rules_by_category(RuleCategory.CODE_STYLE)
    
    def get_testing_requirements(self) -> List[RuleItem]:
        """Get testing and quality requirements"""
        return self.get_rules_by_category(RuleCategory.TESTING)
    
    def get_documentation_standards(self) -> List[RuleItem]:
        """Get documentation requirements"""
        return self.get_rules_by_category(RuleCategory.DOCUMENTATION)
    
    def validate_rules(self) -> List[str]:
        """
        Validate current rule set for consistency and completeness
        
        Returns:
            List of validation errors
        """
        if not self.rule_set:
            return ["No rules loaded"]
        
        return self.rule_set.validate()
    
    def check_rule_compliance(self, file_path: str, file_content: str = None) -> Dict[str, Any]:
        """
        Check compliance of a file against applicable rules
        
        Args:
            file_path: Path to the file to check
            file_content: Optional file content for analysis
            
        Returns:
            Compliance report with violations and suggestions
        """
        applicable_rules = self.get_applicable_rules(file_path)
        
        compliance_report = {
            'file_path': file_path,
            'total_rules': len(applicable_rules),
            'mandatory_violations': [],
            'recommended_suggestions': [],
            'optional_suggestions': [],
            'compliance_score': 0.0
        }
        
        if not applicable_rules:
            compliance_report['compliance_score'] = 1.0
            return compliance_report
        
        # Basic compliance checking (would be enhanced with actual code analysis)
        mandatory_count = 0
        violations = 0
        
        for rule in applicable_rules:
            if rule.priority == RulePriority.MANDATORY:
                mandatory_count += 1
                # Simple pattern matching for basic checks
                if self._check_rule_violation(rule, file_path, file_content):
                    violations += 1
                    compliance_report['mandatory_violations'].append({
                        'rule': rule.content,
                        'category': rule.category.value,
                        'line': rule.source_line
                    })
            elif rule.priority == RulePriority.RECOMMENDED:
                if self._check_rule_violation(rule, file_path, file_content):
                    compliance_report['recommended_suggestions'].append({
                        'rule': rule.content,
                        'category': rule.category.value
                    })
            else:  # Optional
                if self._check_rule_violation(rule, file_path, file_content):
                    compliance_report['optional_suggestions'].append({
                        'rule': rule.content,
                        'category': rule.category.value
                    })
        
        # Calculate compliance score
        if mandatory_count > 0:
            compliance_report['compliance_score'] = (mandatory_count - violations) / mandatory_count
        else:
            compliance_report['compliance_score'] = 1.0
        
        return compliance_report
    
    def _check_rule_violation(self, rule: RuleItem, file_path: str, file_content: str = None) -> bool:
        """
        Check if a specific rule is violated
        
        Args:
            rule: Rule to check
            file_path: Path to the file
            file_content: Optional file content
            
        Returns:
            True if rule is violated
        """
        # This is a simplified implementation
        # In practice, this would use more sophisticated code analysis
        
        if not file_content:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except:
                return False
        
        rule_content = rule.content.lower()
        file_content_lower = file_content.lower()
        
        # Check for technology constraints
        if 'use only' in rule_content:
            # Extract the required technology
            import re
            match = re.search(r'use only (\w+)', rule_content)
            if match:
                required_tech = match.group(1)
                # Check if other competing technologies are used
                competing_techs = {
                    'react': ['vue', 'angular'],
                    'vue': ['react', 'angular'],
                    'angular': ['react', 'vue'],
                    'fastapi': ['flask', 'django'],
                    'flask': ['fastapi', 'django'],
                    'django': ['fastapi', 'flask']
                }
                
                if required_tech in competing_techs:
                    for competing in competing_techs[required_tech]:
                        if competing in file_content_lower:
                            return True
        
        # Check for prohibited technologies
        if any(word in rule_content for word in ['never', 'not', 'avoid', 'prohibited']):
            # Extract prohibited technology
            import re
            match = re.search(r'(?:never|not|avoid|prohibited).*?(\w+)', rule_content)
            if match:
                prohibited_tech = match.group(1)
                if prohibited_tech in file_content_lower:
                    return True
        
        return False
    
    def generate_rules_template(self, project_type: str, context: Dict[str, Any]) -> str:
        """
        Generate a rules template for a project type
        
        Args:
            project_type: Type of project (web_app, data_science, api_service)
            context: Context variables for template generation
            
        Returns:
            Generated rules content
        """
        return self.parser.generate_template(project_type, context)
    
    def create_rules_file(self, project_type: str = None, context: Dict[str, Any] = None) -> bool:
        """
        Create a new rules file with template content
        
        Args:
            project_type: Optional project type for template
            context: Context variables for template
            
        Returns:
            True if file was created successfully
        """
        target_path = os.path.join(self.project_root, self.DEFAULT_RULES_FILENAME)
        
        if os.path.exists(target_path):
            logger.warning(f"Rules file already exists at {target_path}")
            return False
        
        try:
            if project_type and context:
                content = self.generate_rules_template(project_type, context)
            else:
                content = self._get_default_template()
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created rules file at {target_path}")
            self.rules_file_path = target_path
            return True
            
        except Exception as e:
            logger.error(f"Error creating rules file: {e}")
            return False
    
    def _get_default_template(self) -> str:
        """Get default rules template"""
        return """# Project Rules and Context

## Project Overview
Brief description of your project and its main objectives.

## Technology Rules

### Mandatory
- Specify required technologies and frameworks
- Define core technology constraints

### Recommended
- List preferred tools and libraries
- Suggest best practices

### Optional
- Optional technologies to consider
- Nice-to-have tools

## Architecture Rules

### Mandatory
- Core architectural patterns to follow
- Required design principles

### Recommended
- Suggested architectural improvements
- Design pattern recommendations

## Code Style Rules

### Mandatory
- Required coding standards
- Enforced formatting rules

### Recommended
- Preferred coding practices
- Style guidelines

## Testing Rules

### Mandatory
- Required testing standards
- Minimum coverage requirements

### Recommended
- Suggested testing practices
- Quality metrics

## Documentation Rules

### Mandatory
- Required documentation standards
- Essential documentation types

### Recommended
- Additional documentation suggestions
- Documentation tools
"""
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current rules
        
        Returns:
            Summary statistics and information
        """
        if not self.rule_set:
            return {'total_rules': 0, 'categories': {}, 'priorities': {}}
        
        summary = {
            'total_rules': 0,
            'categories': {},
            'priorities': {},
            'groups': len(self.rule_set.groups),
            'has_context_rules': False
        }
        
        all_rules = []
        for group in self.rule_set.groups.values():
            all_rules.extend(group.rules)
        
        summary['total_rules'] = len(all_rules)
        
        # Count by category
        for rule in all_rules:
            category = rule.category.value
            summary['categories'][category] = summary['categories'].get(category, 0) + 1
            
            priority = rule.priority.value if rule.priority else 'unspecified'
            summary['priorities'][priority] = summary['priorities'].get(priority, 0) + 1
            
            if rule.context:
                summary['has_context_rules'] = True
        
        return summary
    
    def get_rules_for_ai_context(self) -> str:
        """
        Get rules formatted for AI context inclusion
        
        Returns:
            Formatted rules string for AI prompts
        """
        if not self.rule_set:
            return "No project-specific rules defined."
        
        lines = [f"# {self.rule_set.name.title()} Rules"]
        
        if self.rule_set.description:
            lines.append(f"\n**Project Description:** {self.rule_set.description}")
        
        # Organize by category and priority
        categories = {}
        for group in self.rule_set.groups.values():
            for rule in group.rules:
                cat_name = rule.category.value.replace('_', ' ').title()
                if cat_name not in categories:
                    categories[cat_name] = {'mandatory': [], 'recommended': [], 'optional': []}
                
                priority = rule.priority.value if rule.priority else 'optional'
                categories[cat_name][priority].append(rule.content)
        
        # Format output
        for category, priorities in categories.items():
            lines.append(f"\n## {category} Rules")
            
            for priority, rules in priorities.items():
                if rules:
                    lines.append(f"\n### {priority.title()}")
                    for rule in rules:
                        lines.append(f"- {rule}")
        
        return "\n".join(lines)
    
    def has_rules(self) -> bool:
        """Check if any rules are defined"""
        return self.rule_set is not None and len(self.rule_set.groups) > 0
    
    def load_template_rules(self, project_type: str, context: Dict[str, Any] = None) -> List[RuleItem]:
        """
        Load rules from a template for a specific project type
        
        Args:
            project_type: Type of project (web_app, data_science, api_service, cli_tool)
            context: Context variables for template generation
            
        Returns:
            List of rules from the template
        """
        if context is None:
            context = {}
            
        # Handle cli_tool as web_app variant
        template_type = project_type
        if project_type == 'cli_tool':
            template_type = 'web_app'  # Use web_app as base for CLI tools
            
        template = self.templates.get(template_type)
        if not template:
            logger.warning(f"No template found for project type: {template_type}")
            return []
        
        try:
            # Generate rules from template
            rule_set = template.generate_rules(context)
            
            # Extract all rules from all groups
            all_rules = []
            for group in rule_set.groups.values():
                all_rules.extend(group.rules)
            
            return all_rules
            
        except Exception as e:
            logger.error(f"Error loading template rules: {e}")
            return []