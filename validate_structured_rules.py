#!/usr/bin/env python3
"""
Quick validation test for structured rules system
"""
import sys
sys.path.append('.')

def test_imports():
    """Test that all components can be imported"""
    print("🧪 Testing Imports...")
    
    try:
        from src.models.rule_models import RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory
        print("✅ Rule models imported successfully")
    except Exception as e:
        print(f"❌ Rule models import failed: {e}")
        return False
    
    try:
        from src.analyzers.structured_rules_suggester import StructuredRulesSuggester
        print("✅ Structured rules suggester imported successfully")
    except Exception as e:
        print(f"❌ Structured rules suggester import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic rule creation and YAML export"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        from src.models.rule_models import RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory
        
        # Create a test rule set
        rule_set = RuleSet(
            name="validation_test",
            version="1.0.0",
            description="Test rule set for validation"
        )
        
        # Create a test group
        group = RuleGroup(
            name="test_group",
            description="Test group",
            category=RuleCategory.TECHNOLOGY
        )
        
        # Create a test rule
        rule = RuleItem(
            content="Use Python 3.8+ for development",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Python version requirement"
        )
        
        group.rules.append(rule)
        rule_set.add_group(group)
        
        # Test YAML export
        yaml_content = rule_set.to_yaml()
        
        print("✅ Rule set created successfully")
        print(f"✅ YAML export successful ({len(yaml_content)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run validation tests"""
    print("🚀 Structured Rules System Validation")
    print("=" * 50)
    
    success = True
    
    # Test imports
    success &= test_imports()
    
    # Test basic functionality
    success &= test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All validation tests passed!")
        print("✅ Structured rules system is working correctly")
    else:
        print("💥 Some validation tests failed!")
        print("❌ Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()
