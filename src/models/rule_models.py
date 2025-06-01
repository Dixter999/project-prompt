"""
Rule Models for ProjectPrompt

This module defines data models for structured rule management with categories,
priorities, and advanced features like inheritance and context-specific rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union
from enum import Enum
import re


class RulePriority(Enum):
    """Rule priority levels"""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class RuleCategory(Enum):
    """Standard rule categories"""
    TECHNOLOGY = "technology"
    ARCHITECTURE = "architecture"
    CODE_STYLE = "code_style"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


@dataclass
class RuleContext:
    """Defines when and where a rule applies"""
    directories: List[str] = field(default_factory=list)
    file_patterns: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    environments: List[str] = field(default_factory=list)  # dev, prod, test


@dataclass
class RuleItem:
    """Individual rule with metadata and context"""
    content: str
    priority: RulePriority
    category: RuleCategory
    description: Optional[str] = None
    context: Optional[RuleContext] = None
    tags: Set[str] = field(default_factory=set)
    source_line: int = 0
    source_file: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    related_rules: List[str] = field(default_factory=list)
    
    def applies_to_file(self, file_path: str) -> bool:
        """Check if this rule applies to the given file path"""
        if not self.context:
            return True
            
        # Check if file is in allowed directories
        if self.context.directories:
            if not any(dir_pattern in file_path for dir_pattern in self.context.directories):
                return False
        
        # Check file patterns
        if self.context.file_patterns:
            import fnmatch
            if not any(fnmatch.fnmatch(file_path, pattern) for pattern in self.context.file_patterns):
                return False
        
        # Check file extensions
        if self.context.file_extensions:
            if not any(file_path.endswith(ext) for ext in self.context.file_extensions):
                return False
        
        # Check exclude patterns
        if self.context.exclude_patterns:
            import fnmatch
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in self.context.exclude_patterns):
                return False
                
        return True


@dataclass
class RuleGroup:
    """Group of rules with common characteristics"""
    name: str
    rules: List[RuleItem] = field(default_factory=list)
    description: Optional[str] = None
    priority: Optional[RulePriority] = None
    category: Optional[RuleCategory] = None
    inherited_from: Optional[str] = None  # Template or parent rule set
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[RuleItem]:
        """Get rules of specific priority"""
        return [rule for rule in self.rules if rule.priority == priority]
    
    def get_applicable_rules(self, file_path: str) -> List[RuleItem]:
        """Get rules that apply to the given file"""
        return [rule for rule in self.rules if rule.applies_to_file(file_path)]


@dataclass
class RuleSet:
    """Complete set of rules for a project"""
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    groups: Dict[str, RuleGroup] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    inheritance: List[str] = field(default_factory=list)  # Inherited rule sets
    
    def add_group(self, group: RuleGroup) -> None:
        """Add a rule group to this set"""
        self.groups[group.name] = group
    
    def get_group(self, name: str) -> Optional[RuleGroup]:
        """Get a rule group by name"""
        return self.groups.get(name)
    
    def get_rules_by_category(self, category: RuleCategory) -> List[RuleItem]:
        """Get all rules of a specific category"""
        rules = []
        for group in self.groups.values():
            rules.extend([rule for rule in group.rules if rule.category == category])
        return rules
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[RuleItem]:
        """Get all rules of a specific priority"""
        rules = []
        for group in self.groups.values():
            rules.extend([rule for rule in group.rules if rule.priority == priority])
        return rules
    
    def get_mandatory_rules(self) -> List[RuleItem]:
        """Get all mandatory rules"""
        return self.get_rules_by_priority(RulePriority.MANDATORY)
    
    def get_applicable_rules(self, file_path: str) -> List[RuleItem]:
        """Get all rules that apply to the given file"""
        rules = []
        for group in self.groups.values():
            rules.extend(group.get_applicable_rules(file_path))
        return rules
    
    def validate(self) -> List[str]:
        """Validate the rule set for consistency and completeness"""
        errors = []
        
        # Check for duplicate rules
        all_rules = []
        for group in self.groups.values():
            all_rules.extend(group.rules)
        
        rule_contents = [rule.content for rule in all_rules]
        duplicates = [content for content in rule_contents if rule_contents.count(content) > 1]
        if duplicates:
            errors.append(f"Duplicate rules found: {set(duplicates)}")
        
        # Check for conflicting rules
        mandatory_rules = self.get_mandatory_rules()
        for rule in mandatory_rules:
            # Check if there are conflicting mandatory rules
            for other_rule in mandatory_rules:
                if rule != other_rule and self._rules_conflict(rule, other_rule):
                    errors.append(f"Conflicting mandatory rules: '{rule.content}' and '{other_rule.content}'")
        
        return errors
    
    def _rules_conflict(self, rule1: RuleItem, rule2: RuleItem) -> bool:
        """Check if two rules potentially conflict"""
        # This is a simple heuristic - in practice, this would be more sophisticated
        conflict_patterns = [
            (r"use only (\w+)", r"use (\w+)"),
            (r"never use (\w+)", r"use (\w+)"),
            (r"must use (\w+)", r"must use (\w+)"),
        ]
        
        for pattern1, pattern2 in conflict_patterns:
            match1 = re.search(pattern1, rule1.content.lower())
            match2 = re.search(pattern2, rule2.content.lower())
            
            if match1 and match2:
                tech1 = match1.group(1)
                tech2 = match2.group(1)
                if tech1 != tech2:
                    return True
        
        return False


@dataclass
class RuleTemplate:
    """Template for generating rules for specific project types"""
    name: str
    project_type: str
    description: str
    rule_groups: List[RuleGroup] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    
    def generate_rules(self, context: Dict[str, Any]) -> RuleSet:
        """Generate a rule set from this template with given context"""
        rule_set = RuleSet(
            name=f"{self.name}_generated",
            description=f"Generated from {self.name} template"
        )
        
        # Replace variables in rules
        for group in self.rule_groups:
            new_group = RuleGroup(
                name=group.name,
                description=group.description,
                priority=group.priority,
                category=group.category
            )
            
            for rule in group.rules:
                content = rule.content
                # Replace template variables
                for var_name, var_value in context.items():
                    content = content.replace(f"{{{var_name}}}", var_value)
                
                new_rule = RuleItem(
                    content=content,
                    priority=rule.priority,
                    category=rule.category,
                    description=rule.description,
                    context=rule.context,
                    tags=rule.tags.copy()
                )
                new_group.rules.append(new_rule)
            
            rule_set.add_group(new_group)
        
        return rule_set


# Predefined rule templates for common project types
def get_web_app_template() -> RuleTemplate:
    """Get template for web application projects"""
    template = RuleTemplate(
        name="web_app",
        project_type="web_application",
        description="Rules template for web applications"
    )
    
    # Technology rules
    tech_group = RuleGroup(
        name="technology",
        category=RuleCategory.TECHNOLOGY,
        description="Technology constraints and requirements"
    )
    
    tech_group.rules.extend([
        RuleItem(
            content="Use {frontend_framework} for all UI components",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Frontend framework requirement"
        ),
        RuleItem(
            content="Use {backend_framework} for API development",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Backend framework requirement"
        ),
        RuleItem(
            content="Use {database} for data persistence",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Database requirement"
        )
    ])
    
    template.rule_groups.append(tech_group)
    return template


def get_data_science_template() -> RuleTemplate:
    """Get template for data science projects"""
    template = RuleTemplate(
        name="data_science",
        project_type="data_science",
        description="Rules template for data science projects"
    )
    
    # Technology rules
    tech_group = RuleGroup(
        name="technology",
        category=RuleCategory.TECHNOLOGY,
        description="Data science technology stack"
    )
    
    tech_group.rules.extend([
        RuleItem(
            content="Use pandas for all data manipulation",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Data manipulation library"
        ),
        RuleItem(
            content="Use jupyter notebooks for exploration",
            priority=RulePriority.RECOMMENDED,
            category=RuleCategory.TECHNOLOGY,
            description="Development environment"
        ),
        RuleItem(
            content="Use {visualization_library} for data visualization",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Visualization library requirement"
        )
    ])
    
    template.rule_groups.append(tech_group)
    return template


def get_api_service_template() -> RuleTemplate:
    """Get template for API service projects"""
    template = RuleTemplate(
        name="api_service",
        project_type="api_service",
        description="Rules template for API services"
    )
    
    # Architecture rules
    arch_group = RuleGroup(
        name="architecture",
        category=RuleCategory.ARCHITECTURE,
        description="API service architecture patterns"
    )
    
    arch_group.rules.extend([
        RuleItem(
            content="All services must inherit from BaseService class",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.ARCHITECTURE,
            description="Service inheritance pattern"
        ),
        RuleItem(
            content="Use dependency injection for external services",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.ARCHITECTURE,
            description="Dependency injection pattern"
        ),
        RuleItem(
            content="Implement proper error handling with custom exceptions",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.ARCHITECTURE,
            description="Error handling pattern"
        )
    ])
    
    template.rule_groups.append(arch_group)
    return template