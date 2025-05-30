"""
Tests for the RulesManager class.

This module contains tests for the RulesManager class which is responsible for
loading, parsing, and accessing project-specific rules.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Import from module
from src.utils.rules_manager import RulesManager, RuleItem, RuleGroup, RuleCategory


class TestRulesManager:
    """Test cases for RulesManager"""

    def test_init(self):
        """Test initialization of RulesManager"""
        rules_manager = RulesManager()
        assert rules_manager is not None
        assert rules_manager.project_root is not None
    
    def test_find_rules_file_not_found(self):
        """Test finding rules file when it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_manager = RulesManager(tmpdir)
            assert rules_manager._find_rules_file() is None
    
    def test_find_rules_file_in_root(self):
        """Test finding rules file in project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a rules file in the temp directory
            rules_path = os.path.join(tmpdir, "project-prompt-rules.md")
            with open(rules_path, "w") as f:
                f.write("# Test Rules")
            
            rules_manager = RulesManager(tmpdir)
            found_path = rules_manager._find_rules_file()
            assert found_path == rules_path
    
    def test_find_rules_file_in_project_output(self):
        """Test finding rules file in project-output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project-output directory
            output_dir = os.path.join(tmpdir, "project-output")
            os.makedirs(output_dir)
            
            # Create a rules file in the project-output directory
            rules_path = os.path.join(output_dir, "project-prompt-rules.md")
            with open(rules_path, "w") as f:
                f.write("# Test Rules")
            
            rules_manager = RulesManager(tmpdir)
            found_path = rules_manager._find_rules_file()
            assert found_path == rules_path
    
    def test_parse_rules_empty(self):
        """Test parsing empty rules content"""
        rules_manager = RulesManager()
        rules_manager._parse_rules("")
        assert rules_manager.rules == {}
    
    def test_parse_rules_basic(self):
        """Test parsing basic rules content"""
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+
- Use FastAPI for API endpoints
        
## Architecture Rules

- Use MVC pattern
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        assert "technology constraints" in rules_manager.rules
        assert "architecture rules" in rules_manager.rules
        
        tech_rules = rules_manager.rules["technology constraints"]
        assert "mandatory" in tech_rules.groups
        assert len(tech_rules.groups["mandatory"].rules) == 2
        
        arch_rules = rules_manager.rules["architecture rules"]
        assert "default" in arch_rules.groups
        assert len(arch_rules.groups["default"].rules) == 1
    
    def test_parse_rules_with_priorities(self):
        """Test parsing rules with different priorities"""
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+

### Recommended
- Use FastAPI
        
### Optional
- Use Redis for caching
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        tech_rules = rules_manager.rules["technology constraints"]
        assert "mandatory" in tech_rules.groups
        assert "recommended" in tech_rules.groups
        assert "optional" in tech_rules.groups
        
        assert len(tech_rules.groups["mandatory"].rules) == 1
        assert len(tech_rules.groups["recommended"].rules) == 1
        assert len(tech_rules.groups["optional"].rules) == 1
    
    def test_get_rules_by_category(self):
        """Test getting rules by category"""
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+
        
## Architecture Rules

- Use MVC pattern
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        tech_rules = rules_manager.get_rules_by_category("technology constraints")
        assert tech_rules is not None
        assert tech_rules.name == "technology constraints"
        
        # Test case insensitive matching
        tech_rules = rules_manager.get_rules_by_category("TECHNOLOGY CONSTRAINTS")
        assert tech_rules is not None
        
        # Test partial matching
        tech_rules = rules_manager.get_rules_by_category("technology")
        assert tech_rules is not None
        
        # Test non-existent category
        non_existent = rules_manager.get_rules_by_category("non-existent")
        assert non_existent is None
    
    def test_get_rules_by_priority(self):
        """Test getting rules by priority"""
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+
        
## Architecture Rules

### Mandatory
- Use MVC pattern
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        mandatory_rules = rules_manager.get_rules_by_priority("mandatory")
        assert len(mandatory_rules) == 2  # Two categories with mandatory rules
        assert "technology constraints" in mandatory_rules
        assert "architecture rules" in mandatory_rules
        
        # Test non-existent priority
        non_existent = rules_manager.get_rules_by_priority("non-existent")
        assert non_existent == {}
    
    def test_get_rules_as_context_string(self):
        """Test generating context string from rules"""
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        context_str = rules_manager.get_rules_as_context_string()
        assert "# Project Rules and Context" in context_str
        assert "## Technology Constraints" in context_str
        assert "### Mandatory" in context_str
        assert "- Use Python 3.8+" in context_str
    
    def test_validate_rules(self):
        """Test rules validation"""
        # Test with valid rules
        content = """# Project Rules
        
## Project Overview
- This is a test project

## Technology Constraints

### Mandatory
- Use Python 3.8+
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        validation_errors = rules_manager.validate_rules()
        assert validation_errors == []
        
        # Test with missing essential category
        content = """# Project Rules
        
## Technology Constraints

### Mandatory
- Use Python 3.8+
"""
        rules_manager = RulesManager()
        rules_manager._parse_rules(content)
        
        validation_errors = rules_manager.validate_rules()
        assert "Missing essential categories" in validation_errors[0]
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="# Template")
    def test_create_default_rules_file(self, mock_file, mock_exists):
        """Test creating default rules file"""
        # Set the file to not exist first
        mock_exists.return_value = False
        
        rules_manager = RulesManager()
        result = rules_manager.create_default_rules_file("/tmp/test.md")
        
        assert result is True
        mock_file.assert_called_with('/tmp/test.md', 'w', encoding='utf-8')


if __name__ == "__main__":
    pytest.main(["-v", __file__])
