#!/usr/bin/env python3
"""
Minimal test for CLI commands to test the rules functionality
"""
import os
import sys
import typer
from rich.console import Console

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

app = typer.Typer()
console = Console()

@app.command()
def test_rules_init():
    """Test the rules initialization"""
    try:
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        
        project_path = os.getcwd()
        manager = EnhancedRulesManager(project_root=project_path)
        
        print("✅ Enhanced Rules Manager imported successfully")
        print(f"📁 Project path: {project_path}")
        
        # Test template creation
        output_file = os.path.join(project_path, "test-rules.md")
        success = manager.create_rules_file_from_template("web_app", output_file)
        
        if success:
            print(f"✅ Rules file created: {output_file}")
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)
                print("🧹 Test file cleaned up")
        else:
            print("❌ Failed to create rules file")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

@app.command()
def test_rules_validate():
    """Test rules validation"""
    try:
        from src.utils.enhanced_rules_manager import EnhancedRulesManager
        
        project_path = os.getcwd()
        manager = EnhancedRulesManager(project_root=project_path)
        
        # Look for existing rules file
        rules_file = os.path.join(project_path, "project-prompt-rules.md")
        if os.path.exists(rules_file):
            print(f"📄 Found rules file: {rules_file}")
            success = manager.load_rules(rules_file)
            if success:
                print("✅ Rules file validation successful")
                summary = manager.get_rules_summary()
                print(f"📊 Total rules: {summary['total_rules']}")
            else:
                print("❌ Rules file validation failed")
        else:
            print("⚠️ No rules file found at project-prompt-rules.md")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    app()
