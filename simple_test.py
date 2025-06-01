#!/usr/bin/env python3
import sys
sys.path.append('.')

print("Starting simple test...")

try:
    from src.models.rule_models import RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory
    print("✅ Rule models imported")
    
    rule_set = RuleSet(name="test", version="1.0", description="test")
    print("✅ RuleSet created")
    
    group = RuleGroup(name="test_group", description="test", category=RuleCategory.TECHNOLOGY)
    print("✅ RuleGroup created")
    
    rule = RuleItem(
        content="Test rule",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TECHNOLOGY,
        description="Test"
    )
    print("✅ RuleItem created")
    
    group.rules.append(rule)
    rule_set.add_group(group)
    print("✅ Rule structure assembled")
    
    yaml_output = rule_set.to_yaml()
    print(f"✅ YAML export successful: {len(yaml_output)} chars")
    
    print("🎉 Simple test passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
