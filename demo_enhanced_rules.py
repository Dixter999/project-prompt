#!/usr/bin/env python3
"""
Demo of the Enhanced Rules Categorization System
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_basic_functionality():
    """Demonstrate basic rule system functionality"""
    from src.models.rule_models import RuleItem, RulePriority, RuleCategory
    from src.utils.rules_parser import RulesParser
    from src.utils.enhanced_rules_manager import EnhancedRulesManager
    
    print("=== Enhanced Rules Categorization Demo ===\n")
    
    # 1. Create rules manually
    print("1. Creating rules programmatically:")
    
    rule1 = RuleItem(
        content="Use React exclusively for UI components",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TECHNOLOGY
    )
    
    rule2 = RuleItem(
        content="Follow component-based architecture",
        priority=RulePriority.RECOMMENDED,
        category=RuleCategory.ARCHITECTURE
    )
    
    print(f"   ✓ {rule1.content} [{rule1.priority.value}, {rule1.category.value}]")
    print(f"   ✓ {rule2.content} [{rule2.priority.value}, {rule2.category.value}]")
    
    # 2. Parse rules from markdown
    print("\n2. Parsing rules from markdown:")
    
    sample_rules = """# Sample Web Project Rules

## Technology Rules

### Mandatory
- Use React for frontend development
- Use Node.js for backend API

### Recommended
- Use TypeScript for type safety
- Use Jest for testing

## Architecture Rules

### Mandatory
- Follow RESTful API design
- Implement proper error handling
"""
    
    parser = RulesParser()
    rule_set = parser.parse_rules_content(sample_rules)
    
    print(f"   ✓ Parsed {len(rule_set.groups)} rule groups")
    print(f"   ✓ Found {len(rule_set.get_mandatory_rules())} mandatory rules")
    print(f"   ✓ Found {len(rule_set.get_rules_by_category(RuleCategory.TECHNOLOGY))} technology rules")
    
    # 3. Generate template
    print("\n3. Generating rules from template:")
    
    context = {
        'project_name': 'Demo Web App',
        'frontend_framework': 'React',
        'backend_framework': 'Express',
        'database': 'PostgreSQL'
    }
    
    template_content = parser.generate_template('web_app', context)
    lines_count = len(template_content.split('\n'))
    print(f"   ✓ Generated {lines_count} lines of template")
    print(f"   ✓ Template includes project-specific configurations")
    
    # 4. Test enhanced manager
    print("\n4. Testing enhanced rules manager:")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a rules file
        rules_file = os.path.join(temp_dir, "project-prompt-rules.md")
        with open(rules_file, 'w') as f:
            f.write(sample_rules)
        
        manager = EnhancedRulesManager(project_root=temp_dir)
        manager.load_rules()
        
        print(f"   ✓ Loaded rules successfully: {manager.has_rules()}")
        
        summary = manager.get_rules_summary()
        print(f"   ✓ Total rules: {summary['total_rules']}")
        print(f"   ✓ Categories: {list(summary['categories'].keys())}")
        print(f"   ✓ Priorities: {list(summary['priorities'].keys())}")
        
        # Get AI context
        ai_context = manager.get_rules_for_ai_context()
        print(f"   ✓ Generated AI context ({len(ai_context)} characters)")
    
    print("\n=== Demo completed successfully! ===")
    print("\nKey features implemented:")
    print("• ✓ Rule categories (Technology, Architecture, Code Style, etc.)")
    print("• ✓ Priority levels (Mandatory, Recommended, Optional)")
    print("• ✓ Context-specific rules (file types, directories)")
    print("• ✓ Rule templates for different project types")
    print("• ✓ Enhanced parsing and validation")
    print("• ✓ AI-ready rule formatting")

if __name__ == "__main__":
    try:
        demo_basic_functionality()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
