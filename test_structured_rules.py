#!/usr/bin/env python3
"""
Test script for structured rules functionality
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append('.')

async def test_structured_rules():
    """Test the structured rules generation"""
    print("🧪 Testing Structured Rules Generation")
    print("=" * 50)
    
    try:
        # Import the suggester
        from src.analyzers.structured_rules_suggester import StructuredRulesSuggester
        print("✅ Successfully imported StructuredRulesSuggester")
        
        # Create suggester instance
        suggester = StructuredRulesSuggester('.')
        print("✅ Successfully created suggester instance")
        
        # Generate rules
        print("🔄 Generating structured rules...")
        rule_set = await suggester.suggest_structured_rules(
            confidence_threshold=0.7,
            use_ai=False,
            project_type=None
        )
        print("✅ Successfully generated rule set")
        
        # Display results
        print(f"\n📊 Results:")
        print(f"  Rule Set Name: {rule_set.name}")
        print(f"  Version: {rule_set.version}")
        print(f"  Description: {rule_set.description}")
        print(f"  Groups: {len(rule_set.groups)}")
        
        total_rules = sum(len(group.rules) for group in rule_set.groups)
        print(f"  Total Rules: {total_rules}")
        
        # Show group breakdown
        print(f"\n📋 Rule Groups:")
        for group in rule_set.groups:
            print(f"  • {group.name}: {len(group.rules)} rules ({group.category.value})")
            
            # Show first 2 rules from each group
            for i, rule in enumerate(group.rules[:2], 1):
                rule_content = rule.content[:60] + "..." if len(rule.content) > 60 else rule.content
                print(f"    {i}. {rule_content}")
                print(f"       Priority: {rule.priority.value}, Category: {rule.category.value}")
            
            if len(group.rules) > 2:
                print(f"       ... and {len(group.rules) - 2} more rules")
            print()
        
        # Test YAML export
        print("🔄 Testing YAML export...")
        yaml_content = rule_set.to_yaml()
        print("✅ Successfully exported to YAML")
        print(f"  YAML length: {len(yaml_content)} characters")
        print(f"  First 200 chars: {yaml_content[:200]}...")
        
        # Save to file
        output_file = "test_structured_rules_output.yaml"
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        print(f"✅ Saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_models():
    """Test the basic rule models"""
    print("\n🧪 Testing Rule Models")
    print("=" * 50)
    
    try:
        from src.models.rule_models import RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory
        
        # Create a simple rule set
        rule_set = RuleSet(
            name="test_rules",
            version="1.0.0",
            description="Test rule set"
        )
        
        group = RuleGroup(
            name="test_group",
            description="Test group",
            category=RuleCategory.TECHNOLOGY
        )
        
        rule = RuleItem(
            content="Use Python 3.8+ for all development",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Python version requirement"
        )
        
        group.rules.append(rule)
        rule_set.add_group(group)
        
        print("✅ Created basic rule structure")
        print(f"  Rule Set: {rule_set.name}")
        print(f"  Groups: {len(rule_set.groups)}")
        print(f"  Rules: {len(rule_set.groups[0].rules)}")
        
        # Test YAML export
        yaml_content = rule_set.to_yaml()
        print("✅ Successfully exported to YAML")
        print(f"  YAML content preview:\n{yaml_content[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Structured Rules Tests")
    print("=" * 50)
    
    # Test basic rule models first
    if test_rule_models():
        print("\n" + "=" * 50)
        # Test full structured rules generation
        result = asyncio.run(test_structured_rules())
        
        if result:
            print("\n🎉 All tests passed successfully!")
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
    else:
        print("\n💥 Basic rule models test failed!")
        sys.exit(1)
