#!/usr/bin/env python3
"""
Quick test of the enhanced rules system
"""

import sys
import os
sys.path.insert(0, '.')

def test_basic_imports():
    print("Testing basic imports...")
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory
        print("✓ Rule models imported")
        
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        print("✓ Enhanced rules manager imported")
        
        from src.utils.rules_parser import RulesParser
        print("✓ Enhanced rules parser imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_rule_creation():
    print("\nTesting rule creation...")
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory
        
        rule = RuleItem(
            content="Use TypeScript for all frontend code",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY
        )
        
        print(f"✓ Created rule: {rule.content}")
        print(f"  Priority: {rule.priority.value}")
        print(f"  Category: {rule.category.value}")
        
        return True
    except Exception as e:
        print(f"✗ Rule creation failed: {e}")
        return False

def test_manager_basic():
    print("\nTesting manager basic functionality...")
    try:
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        
        manager = EnhancedRulesManager()
        print("✓ Manager created")
        
        # Test without loading rules file (should be empty)
        rules = manager.get_all_rules()
        print(f"✓ Got {len(rules)} rules (expected 0 without rules file)")
        
        return True
    except Exception as e:
        print(f"✗ Manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Quick Enhanced Rules Test ===")
    
    tests = [
        test_basic_imports,
        test_rule_creation,
        test_manager_basic
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===")
    
    if passed == len(tests):
        print("🎉 All basic tests passed! Enhanced rules system is working.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
