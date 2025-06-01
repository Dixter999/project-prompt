#!/usr/bin/env python3
"""
Test enhanced rules integration in analyze command
"""

import sys
import os
import tempfile
sys.path.insert(0, '.')

def test_analyze_with_rules():
    print("Testing analyze command with rules integration...")
    
    # Create a temporary directory with a simple project
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temp directory: {temp_dir}")
        
        # Create a simple project structure
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # Create a simple source file
        with open(os.path.join(src_dir, "main.py"), "w") as f:
            f.write("""#!/usr/bin/env python3
def main():
    print("Hello World")

if __name__ == "__main__":
    main()
""")
        
        # Create a package.json file
        with open(os.path.join(temp_dir, "package.json"), "w") as f:
            f.write("""{
  "name": "test-project",
  "version": "1.0.0",
  "main": "src/main.py"
}""")
        
        # Create a simple rules file
        rules_content = """# Project Rules

## Technology Rules

### MANDATORY Technology Constraints
- Use Python 3.8+ for all backend code
- Follow PEP 8 style guidelines
- Include type hints in all functions

### RECOMMENDED Code Style
- Use descriptive variable names
- Add docstrings to all functions
- Keep functions under 50 lines

## Testing Rules

### MANDATORY Testing Requirements
- Write unit tests for all functions
- Achieve minimum 80% code coverage
"""
        
        rules_file = os.path.join(temp_dir, "project-prompt-rules.md")
        with open(rules_file, "w") as f:
            f.write(rules_content)
        
        print(f"✓ Created test project in: {temp_dir}")
        print(f"✓ Created rules file: {rules_file}")
        
        # Test our enhanced rules manager directly (without CLI)
        try:
            from src.utils.enhanced_rules_manager import EnhancedRulesManager
            
            manager = EnhancedRulesManager(project_root=temp_dir)
            success = manager.load_rules()
            
            if success:
                all_rules = manager.get_all_rules()
                print(f"✓ Loaded {len(all_rules)} rules successfully")
                
                # Test compliance checking
                main_file = os.path.join(src_dir, "main.py")
                compliance = manager.check_rule_compliance(main_file)
                
                print(f"✓ Compliance check completed:")
                print(f"  - File: {compliance.get('file_path', 'unknown')}")
                print(f"  - Applicable rules: {compliance.get('applicable_rules_count', 0)}")
                print(f"  - Compliance score: {compliance.get('compliance_score', 0):.1%}")
                
                return True
            else:
                print("✗ Failed to load rules")
                return False
                
        except Exception as e:
            print(f"✗ Error testing rules integration: {e}")
            return False

if __name__ == "__main__":
    print("=== Enhanced Rules Integration Test ===")
    
    if test_analyze_with_rules():
        print("🎉 Enhanced rules integration test passed!")
    else:
        print("❌ Enhanced rules integration test failed!")
