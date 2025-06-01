#!/usr/bin/env python3
"""
Simple test for enhanced rules system
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """Test basic imports"""
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory
        print("✓ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_create_rule():
    """Test creating a basic rule"""
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory
        
        rule = RuleItem(
            content="Use React for UI",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY
        )
        
        print(f"✓ Created rule: {rule.content}")
        print(f"  Priority: {rule.priority.value}")
        print(f"  Category: {rule.category.value}")
        return True
    except Exception as e:
        print(f"❌ Rule creation failed: {e}")
        return False

def test_parser_import():
    """Test parser import"""
    try:
        from src.utils.rules_parser import RulesParser
        parser = RulesParser()
        print("✓ Parser import successful")
        return True
    except ImportError as e:
        print(f"❌ Parser import failed: {e}")
        return False

def test_manager_import():
    """Test manager import"""
    try:
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        manager = EnhancedRulesManager()
        print("✓ Manager import successful")
        return True
    except ImportError as e:
        print(f"❌ Manager import failed: {e}")
        return False

if __name__ == "__main__":
    print("Running simple enhanced rules test...\n")
    
    tests = [
        test_basic_import,
        test_create_rule,
        test_parser_import,
        test_manager_import
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All basic tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
