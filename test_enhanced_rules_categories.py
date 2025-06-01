"""
Test the enhanced rules categorization system

This test file validates the new rule models, parser, and enhanced manager
to ensure they work correctly with categories, priorities, and templates.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.rule_models import (
    RuleSet, RuleGroup, RuleItem, RuleContext,
    RulePriority, RuleCategory,
    get_web_app_template, get_data_science_template, get_api_service_template
)
from src.utils.rules_parser import RulesParser
from src.utils.enhanced_rules_manager import EnhancedRulesManager


def test_rule_models():
    """Test the basic rule model functionality"""
    print("Testing rule models...")
    
    # Create a rule item
    rule = RuleItem(
        content="Use React exclusively for UI components",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TECHNOLOGY,
        description="Frontend framework requirement"
    )
    
    assert rule.content == "Use React exclusively for UI components"
    assert rule.priority == RulePriority.MANDATORY
    assert rule.category == RuleCategory.TECHNOLOGY
    
    # Test rule group
    group = RuleGroup(name="technology", category=RuleCategory.TECHNOLOGY)
    group.rules.append(rule)
    
    mandatory_rules = group.get_rules_by_priority(RulePriority.MANDATORY)
    assert len(mandatory_rules) == 1
    assert mandatory_rules[0] == rule
    
    # Test rule set
    rule_set = RuleSet(name="test_project", version="1.0.0")
    rule_set.add_group(group)
    
    tech_rules = rule_set.get_rules_by_category(RuleCategory.TECHNOLOGY)
    assert len(tech_rules) == 1
    assert tech_rules[0] == rule
    
    print("✓ Rule models working correctly")


def test_rule_context():
    """Test context-specific rules functionality"""
    print("Testing rule context...")
    
    # Create context for React files only
    context = RuleContext(
        file_extensions=['.jsx', '.tsx'],
        directories=['src/components', 'src/pages'],
        exclude_patterns=['*.test.*']
    )
    
    rule = RuleItem(
        content="Use functional components with hooks",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.ARCHITECTURE,
        context=context
    )
    
    # Test file matching
    assert rule.applies_to_file('src/components/Button.jsx') == True
    assert rule.applies_to_file('src/components/Button.tsx') == True
    assert rule.applies_to_file('src/utils/helper.js') == False
    assert rule.applies_to_file('src/components/Button.test.jsx') == False
    
    print("✓ Rule context working correctly")


def test_rules_parser():
    """Test the enhanced rules parser"""
    print("Testing enhanced rules parser...")
    
    # Create test rules content
    rules_content = """# Test Project Rules

## Project Overview
A test project for validating rules parsing.

## Technology Rules

### Mandatory
- Use React exclusively for UI components [files: *.jsx, *.tsx]
- Use TypeScript for type safety
- Use PostgreSQL for database operations

### Recommended
- Use Redux for state management
- Use Jest for testing

### Optional
- Consider using Storybook for documentation

## Architecture Rules

### Mandatory
- Follow component-based architecture
- Use dependency injection pattern

## Code Style Rules

### Recommended
- Use consistent naming conventions
- Follow PEP 8 guidelines
"""
    
    parser = RulesParser()
    rule_set = parser.parse_rules_content(rules_content)
    
    assert rule_set.name == "test_project_rules"
    assert len(rule_set.groups) >= 3  # technology, architecture, code_style
    
    # Check technology rules
    tech_rules = rule_set.get_rules_by_category(RuleCategory.TECHNOLOGY)
    assert len(tech_rules) >= 3
    
    # Check priorities
    mandatory_rules = rule_set.get_mandatory_rules()
    assert len(mandatory_rules) >= 2
    
    print("✓ Rules parser working correctly")


def test_template_generation():
    """Test rule template generation"""
    print("Testing template generation...")
    
    # Test web app template
    web_template = get_web_app_template()
    assert web_template.name == "web_app"
    assert web_template.project_type == "web_application"
    
    # Generate rules from template
    context = {
        'frontend_framework': 'React',
        'backend_framework': 'Node.js',
        'database': 'PostgreSQL'
    }
    
    generated_rules = web_template.generate_rules(context)
    assert generated_rules.name == "web_app_generated"
    
    # Check that template variables were replaced
    all_rules = []
    for group in generated_rules.groups.values():
        all_rules.extend(group.rules)
    
    react_rules = [r for r in all_rules if 'React' in r.content]
    assert len(react_rules) > 0
    
    print("✓ Template generation working correctly")


def test_enhanced_rules_manager():
    """Test the enhanced rules manager"""
    print("Testing enhanced rules manager...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test rules file
        rules_file = os.path.join(temp_dir, "project-prompt-rules.md")
        
        test_rules = """# Enhanced Test Project

## Project Overview
Testing the enhanced rules manager functionality.

## Technology Rules

### Mandatory
- Use Python 3.8+ for all development
- Use FastAPI for API development
- Use PostgreSQL for database

### Recommended
- Use pytest for testing
- Use black for code formatting

## Architecture Rules

### Mandatory
- Follow clean architecture principles
- Use dependency injection

### Recommended
- Implement proper logging
- Use design patterns appropriately

## Testing Rules

### Mandatory
- Minimum 80% code coverage
- All APIs must have tests

### Recommended
- Use TDD approach
- Implement integration tests
"""
        
        with open(rules_file, 'w') as f:
            f.write(test_rules)
        
        # Test enhanced rules manager
        manager = EnhancedRulesManager(project_root=temp_dir)
        
        # Test loading
        assert manager.load_rules() == True
        assert manager.has_rules() == True
        
        # Test category access
        tech_rules = manager.get_rules_by_category(RuleCategory.TECHNOLOGY)
        assert len(tech_rules) >= 3
        
        # Test priority access
        mandatory_rules = manager.get_mandatory_rules()
        assert len(mandatory_rules) >= 4
        
        # Test compliance checking
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('hello world')")
        
        compliance = manager.check_rule_compliance(test_file)
        assert 'file_path' in compliance
        assert 'compliance_score' in compliance
        
        # Test AI context generation
        ai_context = manager.get_rules_for_ai_context()
        assert "Enhanced Test Project" in ai_context
        assert "Technology Rules" in ai_context
        
        # Test rules summary
        summary = manager.get_rules_summary()
        assert summary['total_rules'] > 0
        assert 'categories' in summary
        assert 'priorities' in summary
        
        print("✓ Enhanced rules manager working correctly")


def test_validation():
    """Test rules validation functionality"""
    print("Testing rules validation...")
    
    parser = RulesParser()
    
    # Test valid rules
    valid_rules = """# Valid Project

## Technology Rules

### Mandatory
- Use React for frontend
- Use Node.js for backend

## Architecture Rules

### Recommended
- Follow MVC pattern
"""
    
    errors = parser.validate_syntax(valid_rules)
    assert len(errors) == 0
    
    # Test invalid rules
    invalid_rules = """# Invalid Project

This has no proper categories or rules.
"""
    
    errors = parser.validate_syntax(invalid_rules)
    assert len(errors) > 0
    
    print("✓ Rules validation working correctly")


def test_file_applicability():
    """Test file-specific rule application"""
    print("Testing file applicability...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = EnhancedRulesManager(project_root=temp_dir)
        
        # Create test files
        js_file = os.path.join(temp_dir, "component.jsx")
        py_file = os.path.join(temp_dir, "script.py")
        
        with open(js_file, 'w') as f:
            f.write("const Component = () => <div>Hello</div>;")
        
        with open(py_file, 'w') as f:
            f.write("def hello(): print('hello')")
        
        # This would test file-specific rules if we had them loaded
        js_rules = manager.get_applicable_rules(js_file)
        py_rules = manager.get_applicable_rules(py_file)
        
        # Since we don't have context-specific rules in this test,
        # both should return the same (empty) set
        assert isinstance(js_rules, list)
        assert isinstance(py_rules, list)
        
        print("✓ File applicability working correctly")


if __name__ == "__main__":
    print("Running enhanced rules categorization tests...\n")
    
    try:
        test_rule_models()
        test_rule_context()
        test_rules_parser()
        test_template_generation()
        test_enhanced_rules_manager()
        test_validation()
        test_file_applicability()
        
        print("\n🎉 All tests passed! Enhanced rules categorization system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
