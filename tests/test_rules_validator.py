"""
Tests for the RulesValidator class.

This module contains tests for the RulesValidator class which is responsible for
validating the syntax and structure of project rules.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Import from module
from src.utils.rules_manager import RulesManager, RuleItem, RuleGroup, RuleCategory
from src.validators.rules_validator import RulesValidator


class TestRulesValidator:
    """Test cases for RulesValidator"""

    def test_init(self):
        """Test initialization of RulesValidator"""
        # Test with default RulesManager
        validator = RulesValidator()
        assert validator is not None
        assert validator.rules_manager is not None
        
        # Test with custom RulesManager
        mock_manager = MagicMock()
        validator = RulesValidator(mock_manager)
        assert validator.rules_manager == mock_manager
    
    def test_validate_no_rules(self):
        """Test validation when no rules are found"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = False
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is False
        assert len(validator.errors) == 1
        assert "No rules file found" in validator.errors[0]
    
    def test_validate_missing_required_categories(self):
        """Test validation with missing required categories"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        mock_manager.get_all_rules.return_value = {
            "technology constraints": RuleCategory(
                name="technology constraints", 
                groups={"mandatory": RuleGroup(rules=[RuleItem(content="Use Python")])}
            )
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is False
        assert any("Missing required categories" in error for error in validator.errors)
    
    def test_validate_empty_category(self):
        """Test validation with an empty category"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        mock_manager.get_all_rules.return_value = {
            "project overview": RuleCategory(
                name="project overview", 
                groups={"default": RuleGroup(rules=[RuleItem(content="Overview")])}
            ),
            "empty category": RuleCategory(
                name="empty category",
                groups={}  # Empty groups
            )
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is True  # No errors, just warnings
        assert any("doesn't have any rules" in warning for warning in validator.warnings)
    
    def test_validate_empty_priority_group(self):
        """Test validation with an empty priority group"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        mock_manager.get_all_rules.return_value = {
            "project overview": RuleCategory(
                name="project overview", 
                groups={"default": RuleGroup(rules=[RuleItem(content="Overview")])}
            ),
            "technology constraints": RuleCategory(
                name="technology constraints",
                groups={"mandatory": RuleGroup(rules=[]), "recommended": RuleGroup(rules=[RuleItem(content="Use Python")])}
            )
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is True  # No errors, just warnings
        assert any("doesn't have any rules" in warning for warning in validator.warnings)
    
    def test_validate_missing_mandatory_priorities(self):
        """Test validation with recommended categories missing mandatory priorities"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        mock_manager.get_all_rules.return_value = {
            "project overview": RuleCategory(
                name="project overview", 
                groups={"default": RuleGroup(rules=[RuleItem(content="Overview")])}
            ),
            "technology constraints": RuleCategory(
                name="technology constraints",
                groups={"recommended": RuleGroup(rules=[RuleItem(content="Use Python")])}  # Missing mandatory group
            )
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is True  # No errors, just warnings
        assert any("should have mandatory rules" in warning for warning in validator.warnings)
    
    def test_validate_empty_rule(self):
        """Test validation with empty rule content"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        mock_manager.get_all_rules.return_value = {
            "project overview": RuleCategory(
                name="project overview", 
                groups={"default": RuleGroup(rules=[RuleItem(content="")])}  # Empty rule content
            )
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is False
        assert any("Empty rule" in error for error in validator.errors)
    
    def test_check_for_conflicts(self):
        """Test validation with conflicting technology rules"""
        mock_manager = MagicMock()
        mock_manager.has_rules.return_value = True
        
        # Create rules with conflicts (same technology in mandatory and prohibited)
        tech_category = RuleCategory(
            name="technology constraints",
            groups={
                "mandatory": RuleGroup(rules=[
                    RuleItem(content="Use **Flask** for APIs")
                ]),
                "prohibited": RuleGroup(rules=[
                    RuleItem(content="Do NOT use Flask")
                ])
            }
        )
        
        mock_manager.get_all_rules.return_value = {
            "project overview": RuleCategory(
                name="project overview", 
                groups={"default": RuleGroup(rules=[RuleItem(content="Overview")])}
            ),
            "technology constraints": tech_category
        }
        
        validator = RulesValidator(mock_manager)
        result = validator.validate()
        
        assert result is False
        assert any("Conflicting technology rules" in error for error in validator.errors)
    
    def test_extract_technology_name(self):
        """Test extracting technology names from rule content"""
        validator = RulesValidator()
        
        # Test different patterns
        assert validator._extract_technology_name("Use Flask for APIs") == "Flask"
        assert validator._extract_technology_name("Flask is required") == "Flask"
        assert validator._extract_technology_name("Do NOT use Django") == "Django"
        assert validator._extract_technology_name("**PostgreSQL** with SQLAlchemy") == "PostgreSQL"
        assert validator._extract_technology_name("Simple text") is None
    
    def test_get_validation_report(self):
        """Test getting validation report"""
        validator = RulesValidator()
        
        # Test with no errors or warnings
        assert "passed with no issues" in validator.get_validation_report()
        
        # Test with errors
        validator.errors = ["Error 1", "Error 2"]
        report = validator.get_validation_report()
        assert "## Errors" in report
        assert "- Error 1" in report
        assert "- Error 2" in report
        assert "validation failed" in report
        
        # Test with warnings
        validator.errors = []
        validator.warnings = ["Warning 1", "Warning 2"]
        report = validator.get_validation_report()
        assert "## Warnings" in report
        assert "- Warning 1" in report
        assert "- Warning 2" in report
        assert "passed with warnings" in report
        
        # Test with both errors and warnings
        validator.errors = ["Error 1"]
        validator.warnings = ["Warning 1"]
        report = validator.get_validation_report()
        assert "## Errors" in report
        assert "## Warnings" in report
        assert "validation failed" in report


if __name__ == "__main__":
    pytest.main(["-v", __file__])
