"""
Rules Validator for ProjectPrompt

This module provides validation functionality for project rules,
ensuring they follow the required format and structure.
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from ..utils.rules_manager import RulesManager, RuleCategory, RuleGroup, RuleItem

# Configure logger
logger = logging.getLogger(__name__)

class RulesValidator:
    """
    Validates the syntax and structure of project rules.
    
    This class checks:
    - Required categories are present
    - Rules have proper structure
    - No conflicting rules exist
    - Rules follow the expected format
    """
    
    # Required rule categories
    REQUIRED_CATEGORIES = {"project overview"}
    
    # Categories that should have mandatory rules
    RECOMMENDED_WITH_MANDATORY = {"technology constraints", "architecture rules"}
    
    def __init__(self, rules_manager: RulesManager = None):
        """
        Initialize the validator with an optional rules manager
        
        Args:
            rules_manager: RulesManager instance to use.
                          If None, a new one is created.
        """
        self.rules_manager = rules_manager or RulesManager()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """
        Validate rules and collect errors/warnings
        
        Returns:
            True if validation passed with no errors, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Skip validation if no rules are found
        if not self.rules_manager.has_rules():
            self.errors.append("No rules file found or it's empty")
            return False
        
        # Get all rules
        rules = self.rules_manager.get_all_rules()
        
        # Check for required categories
        self._check_required_categories(rules)
        
        # Check each category's structure
        for category_name, category in rules.items():
            self._validate_category(category_name, category)
        
        # Check for conflicting rules
        self._check_for_conflicts(rules)
        
        # Return True only if no errors (warnings are acceptable)
        return len(self.errors) == 0
    
    def _check_required_categories(self, rules: Dict[str, RuleCategory]) -> None:
        """
        Check if all required categories are present
        
        Args:
            rules: Dictionary of rule categories
        """
        missing_categories = [cat for cat in self.REQUIRED_CATEGORIES
                             if cat not in rules]
        
        if missing_categories:
            self.errors.append(
                f"Missing required categories: {', '.join(missing_categories)}"
            )
        
        # Check for recommended categories with mandatory rules
        for category in self.RECOMMENDED_WITH_MANDATORY:
            if category in rules:
                rule_cat = rules[category]
                if "mandatory" not in rule_cat.groups:
                    self.warnings.append(
                        f"Category '{category}' should have mandatory rules defined"
                    )
    
    def _validate_category(self, name: str, category: RuleCategory) -> None:
        """
        Validate the structure of a single category
        
        Args:
            name: Category name
            category: RuleCategory object
        """
        # Check if category has any rules
        if not category.groups:
            self.warnings.append(f"Category '{name}' doesn't have any rules")
            return
        
        # Check each priority group
        for priority, group in category.groups.items():
            if not group.rules:
                self.warnings.append(
                    f"Priority '{priority}' in category '{name}' doesn't have any rules"
                )
                continue
            
            # Validate individual rules
            for rule in group.rules:
                self._validate_rule(rule)
    
    def _validate_rule(self, rule: RuleItem) -> None:
        """
        Validate a single rule item
        
        Args:
            rule: RuleItem to validate
        """
        # Check if rule has content
        if not rule.content:
            self.errors.append(f"Empty rule in category '{rule.category}'")
            return
        
        # Additional rule-specific validations can be added here
        # For example, check for proper formatting, forbidden patterns, etc.
    
    def _check_for_conflicts(self, rules: Dict[str, RuleCategory]) -> None:
        """
        Check for conflicting rules across categories
        
        Args:
            rules: Dictionary of rule categories
        """
        # Example: Check for technology constraints that conflict with each other
        if "technology constraints" in rules:
            tech_rules = rules["technology constraints"]
            
            # Extract mandatory and prohibited technologies
            mandatory_techs = set()
            prohibited_techs = set()
            
            # Check mandatory technologies
            if "mandatory" in tech_rules.groups:
                for rule in tech_rules.groups["mandatory"].rules:
                    # Extract technology name from rule content
                    # This is a simplistic approach and might need refinement
                    tech_name = self._extract_technology_name(rule.content)
                    if tech_name:
                        mandatory_techs.add(tech_name.lower())
            
            # Check prohibited technologies
            if "prohibited" in tech_rules.groups:
                for rule in tech_rules.groups["prohibited"].rules:
                    tech_name = self._extract_technology_name(rule.content)
                    if tech_name:
                        prohibited_techs.add(tech_name.lower())
            
            # Find conflicts
            conflicts = mandatory_techs.intersection(prohibited_techs)
            if conflicts:
                self.errors.append(
                    f"Conflicting technology rules: {', '.join(conflicts)} "
                    "are both mandatory and prohibited"
                )
    
    def _extract_technology_name(self, rule_content: str) -> Optional[str]:
        """
        Extract a technology name from a rule content string
        
        Args:
            rule_content: The rule content text
            
        Returns:
            Technology name if found, None otherwise
        """
        # This is a simplified extraction method
        # A more sophisticated approach might use NLP or pattern matching
        
        # Try to extract technology name from patterns like:
        # - Use X for Y
        # - X is required
        # - Do NOT use X
        
        # Pattern 1: Use X for Y
        match = re.search(r"Use\s+(\w+)", rule_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 2: X is required
        match = re.search(r"(\w+)\s+is required", rule_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: Do NOT use X
        match = re.search(r"Do NOT use\s+(\w+)", rule_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Extract text between ** if exists (for bold text)
        match = re.search(r"\*\*([^*]+)\*\*", rule_content)
        if match:
            return match.group(1)
        
        return None
    
    def get_validation_report(self) -> str:
        """
        Get a formatted report of validation results
        
        Returns:
            Formatted string with validation results
        """
        if not self.errors and not self.warnings:
            return "Rules validation passed with no issues."
        
        lines = ["# Rules Validation Report"]
        
        if self.errors:
            lines.append("\n## Errors")
            for error in self.errors:
                lines.append(f"- {error}")
        
        if self.warnings:
            lines.append("\n## Warnings")
            for warning in self.warnings:
                lines.append(f"- {warning}")
        
        if not self.errors:
            lines.append("\n## Summary: Rules validation passed with warnings.")
        else:
            lines.append("\n## Summary: Rules validation failed. Please fix the errors.")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Test validation
    rules_manager = RulesManager()
    validator = RulesValidator(rules_manager)
    
    if validator.validate():
        print("Validation successful!")
    else:
        print(validator.get_validation_report())
