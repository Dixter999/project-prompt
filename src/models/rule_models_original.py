"""
Rule Models for ProjectPrompt

This module defines the data models for advanced rule categorization and priority management.
Supports technology constraints, architecture patterns, code style preferences, 
testing requirements, and documentation standards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union
from enum import Enum
import json

class RulePriority(Enum):
    """Rule priority levels"""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"

class RuleCategory(Enum):
    """Standard rule categories"""
    PROJECT_OVERVIEW = "project overview"
    TECHNOLOGY_CONSTRAINTS = "technology constraints"
    ARCHITECTURE_RULES = "architecture rules"
    CODE_STYLE = "code style requirements"
    TESTING_REQUIREMENTS = "testing requirements"
    DOCUMENTATION_STANDARDS = "documentation standards"
    AI_ANALYSIS_PREFERENCES = "ai analysis preferences"
    CUSTOM_ANALYSIS_RULES = "custom analysis rules"
    FILE_ORGANIZATION = "file organization"
    NAMING_CONVENTIONS = "naming conventions"
    ERROR_HANDLING = "error handling"
    PERFORMANCE_REQUIREMENTS = "performance requirements"
    SECURITY_RULES = "security rules"
    DEPLOYMENT_RULES = "deployment rules"

@dataclass
class RuleConstraint:
    """Represents a specific constraint or requirement"""
    description: str
    applies_to: Optional[List[str]] = None  # File patterns, directories, or contexts
    exceptions: Optional[List[str]] = None  # Exceptions to the rule
    rationale: Optional[str] = None  # Why this rule exists
    examples: Optional[List[str]] = None  # Examples of good/bad practice
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "description": self.description,
            "applies_to": self.applies_to,
            "exceptions": self.exceptions,
            "rationale": self.rationale,
            "examples": self.examples
        }

@dataclass
class TechnologyConstraint(RuleConstraint):
    """Technology-specific constraints"""
    technology_type: str = ""  # framework, library, database, etc.
    version_requirement: Optional[str] = None
    alternatives: Optional[List[str]] = None
    prohibited: bool = False

@dataclass
class ArchitectureRule(RuleConstraint):
    """Architecture pattern requirements"""
    pattern_type: str = ""  # MVC, microservices, layered, etc.
    implementation_details: Optional[Dict[str, str]] = None
    dependencies: Optional[List[str]] = None  # Other patterns this depends on

@dataclass
class CodeStyleRule(RuleConstraint):
    """Code style and formatting requirements"""
    language: Optional[str] = None
    tool_config: Optional[Dict[str, Any]] = None  # Linter/formatter config
    metrics: Optional[Dict[str, Union[int, str]]] = None  # Complexity, length limits

@dataclass
class TestingRule(RuleConstraint):
    """Testing requirements and standards"""
    test_type: str = ""  # unit, integration, e2e, performance
    coverage_requirement: Optional[float] = None
    tools_required: Optional[List[str]] = None
    patterns: Optional[List[str]] = None

@dataclass
class DocumentationRule(RuleConstraint):
    """Documentation requirements"""
    doc_type: str = ""  # code, api, user, architectural
    format: Optional[str] = None  # markdown, restructured text, etc.
    minimum_content: Optional[List[str]] = None
    tools: Optional[List[str]] = None

@dataclass
class RulePriorityGroup:
    """Group of rules with the same priority level"""
    priority: RulePriority
    rules: List[RuleConstraint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_rule(self, rule: RuleConstraint) -> None:
        """Add a rule to this priority group"""
        self.rules.append(rule)
    
    def get_rules_by_type(self, rule_type: type) -> List[RuleConstraint]:
        """Get rules of a specific type"""
        return [rule for rule in self.rules if isinstance(rule, rule_type)]

@dataclass
class RuleCategoryGroup:
    """Collection of rules organized by category and priority"""
    category: RuleCategory
    priority_groups: Dict[RulePriority, RulePriorityGroup] = field(default_factory=dict)
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_rule(self, rule: RuleConstraint, priority: RulePriority) -> None:
        """Add a rule with specified priority"""
        if priority not in self.priority_groups:
            self.priority_groups[priority] = RulePriorityGroup(priority=priority)
        self.priority_groups[priority].add_rule(rule)
    
    def get_mandatory_rules(self) -> List[RuleConstraint]:
        """Get all mandatory rules in this category"""
        if RulePriority.MANDATORY in self.priority_groups:
            return self.priority_groups[RulePriority.MANDATORY].rules
        return []
    
    def get_recommended_rules(self) -> List[RuleConstraint]:
        """Get all recommended rules in this category"""
        if RulePriority.RECOMMENDED in self.priority_groups:
            return self.priority_groups[RulePriority.RECOMMENDED].rules
        return []
    
    def get_optional_rules(self) -> List[RuleConstraint]:
        """Get all optional rules in this category"""
        if RulePriority.OPTIONAL in self.priority_groups:
            return self.priority_groups[RulePriority.OPTIONAL].rules
        return []
    
    def get_all_rules(self) -> List[RuleConstraint]:
        """Get all rules regardless of priority"""
        all_rules = []
        for group in self.priority_groups.values():
            all_rules.extend(group.rules)
        return all_rules

@dataclass
class ProjectRuleSet:
    """Complete set of rules for a project"""
    categories: Dict[RuleCategory, RuleCategoryGroup] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    
    def add_category(self, category: RuleCategory, description: Optional[str] = None) -> RuleCategoryGroup:
        """Add or get a rule category"""
        if category not in self.categories:
            self.categories[category] = RuleCategoryGroup(category=category, description=description)
        return self.categories[category]
    
    def add_rule(self, category: RuleCategory, rule: RuleConstraint, priority: RulePriority) -> None:
        """Add a rule to a specific category and priority"""
        category_group = self.add_category(category)
        category_group.add_rule(rule, priority)
    
    def get_mandatory_rules(self) -> Dict[RuleCategory, List[RuleConstraint]]:
        """Get all mandatory rules across categories"""
        mandatory = {}
        for category, group in self.categories.items():
            rules = group.get_mandatory_rules()
            if rules:
                mandatory[category] = rules
        return mandatory
    
    def get_rules_by_category(self, category: RuleCategory) -> Optional[RuleCategoryGroup]:
        """Get all rules for a specific category"""
        return self.categories.get(category)
    
    def get_rules_by_priority(self, priority: RulePriority) -> Dict[RuleCategory, List[RuleConstraint]]:
        """Get all rules of a specific priority across categories"""
        result = {}
        for category, group in self.categories.items():
            if priority in group.priority_groups:
                rules = group.priority_groups[priority].rules
                if rules:
                    result[category] = rules
        return result
    
    def validate_structure(self) -> List[str]:
        """Validate the rule set structure and return any issues"""
        issues = []
        
        # Check for required categories
        required = {RuleCategory.PROJECT_OVERVIEW}
        missing = required - set(self.categories.keys())
        if missing:
            issues.append(f"Missing required categories: {[cat.value for cat in missing]}")
        
        # Check each category for basic structure
        for category, group in self.categories.items():
            if not group.priority_groups:
                issues.append(f"Category '{category.value}' has no rules")
            
            # Check for empty priority groups
            for priority, priority_group in group.priority_groups.items():
                if not priority_group.rules:
                    issues.append(f"Category '{category.value}' has empty {priority.value} group")
        
        return issues
    
    def to_markdown(self) -> str:
        """Convert the rule set to markdown format"""
        lines = ["# Project Rules and Context\n"]
        
        # Sort categories for consistent output
        sorted_categories = sorted(self.categories.items(), key=lambda x: x[0].value)
        
        for category, group in sorted_categories:
            lines.append(f"## {category.value.title()}")
            if group.description:
                lines.append(f"{group.description}\n")
            
            # Sort priorities: mandatory, recommended, optional
            priority_order = [RulePriority.MANDATORY, RulePriority.RECOMMENDED, RulePriority.OPTIONAL]
            
            for priority in priority_order:
                if priority in group.priority_groups:
                    priority_group = group.priority_groups[priority]
                    if priority_group.rules:
                        lines.append(f"### {priority.value.title()}")
                        for rule in priority_group.rules:
                            lines.append(f"- {rule.description}")
                            if rule.rationale:
                                lines.append(f"  - *Rationale: {rule.rationale}*")
                            if rule.examples:
                                lines.append(f"  - *Examples: {', '.join(rule.examples)}*")
                        lines.append("")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def to_context_string(self) -> str:
        """Convert to a context string for AI analysis"""
        return self.to_markdown()
