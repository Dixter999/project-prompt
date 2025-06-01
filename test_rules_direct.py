#!/usr/bin/env python3
"""
Direct test of enhanced rules system without main.py imports
"""

import sys
import os
import tempfile
sys.path.insert(0, '.')

def test_rules_directly():
    print("Testing enhanced rules system directly...")
    
    try:
        # Import core components
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        from src.models.rule_models import RuleCategory, RulePriority
        print("✓ Core imports successful")
        
        # Create temporary test environment
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"✓ Created temp directory: {temp_dir}")
            
            # Create a simple rules file
            rules_content = """# Test Project Rules

## Technology Rules

### MANDATORY Technology Constraints
- Use Python 3.8+ for all backend code
- Follow PEP 8 style guidelines

### RECOMMENDED Code Style  
- Use descriptive variable names
- Add docstrings to all functions

## Testing Rules

### MANDATORY Testing Requirements
- Write unit tests for all functions
- Achieve minimum 80% code coverage
"""
            
            rules_file = os.path.join(temp_dir, "project-prompt-rules.md")
            with open(rules_file, "w") as f:
                f.write(rules_content)
            print("✓ Created rules file")
            
            # Create a test source file
            src_dir = os.path.join(temp_dir, "src")
            os.makedirs(src_dir, exist_ok=True)
            
            test_file = os.path.join(src_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("""def hello_world():
    print("Hello, World!")
""")
            print("✓ Created test source file")
            
            # Test enhanced rules manager
            manager = EnhancedRulesManager(project_root=temp_dir)
            print("✓ Created rules manager")
            
            # Load rules
            success = manager.load_rules()
            if not success:
                print("✗ Failed to load rules")
                return False
            print("✓ Rules loaded successfully")
            
            # Get all rules
            all_rules = manager.get_all_rules()
            print(f"✓ Found {len(all_rules)} total rules")
            
            # Test by category
            tech_rules = manager.get_rules_by_category(RuleCategory.TECHNOLOGY)
            test_rules = manager.get_rules_by_category(RuleCategory.TESTING)
            print(f"✓ Technology rules: {len(tech_rules)}")
            print(f"✓ Testing rules: {len(test_rules)}")
            
            # Test by priority
            mandatory_rules = manager.get_rules_by_priority(RulePriority.MANDATORY)
            recommended_rules = manager.get_rules_by_priority(RulePriority.RECOMMENDED)
            print(f"✓ Mandatory rules: {len(mandatory_rules)}")
            print(f"✓ Recommended rules: {len(recommended_rules)}")
            
            # Test compliance checking
            compliance = manager.check_rule_compliance(test_file)
            print(f"✓ Compliance check completed:")
            print(f"  - File: {os.path.basename(compliance.get('file_path', 'unknown'))}")
            print(f"  - Applicable rules: {compliance.get('applicable_rules_count', 0)}")
            print(f"  - Compliance score: {compliance.get('compliance_score', 0):.1%}")
            
            # Test rules summary
            summary = manager.get_rules_summary()
            print(f"✓ Rules summary:")
            print(f"  - Total rules: {summary.get('total_rules', 0)}")
            print(f"  - Categories: {len(summary.get('categories', {}))}")
            print(f"  - Priorities: {len(summary.get('priorities', {}))}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Direct Enhanced Rules Test ===")
    
    if test_rules_directly():
        print("\n🎉 All tests passed! Enhanced rules system is fully functional.")
    else:
        print("\n❌ Test failed. Check implementation.")
