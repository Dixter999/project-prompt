#!/usr/bin/env python3
"""
Phase 4 Validation Script
Tests the complete CLI implementation and validates all features
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import json

def run_command(cmd, description, check_returncode=True):
    """Run a command and capture output"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check_returncode and result.returncode != 0:
            print(f"   ❌ Failed: {result.stderr}")
            return False, result.stderr
        else:
            print(f"   ✅ Success")
            return True, result.stdout
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, str(e)

def create_test_project():
    """Create a test project for validation"""
    test_dir = Path(tempfile.mkdtemp(prefix="projectprompt_test_"))
    
    # Create test files
    (test_dir / "app.py").write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World"

if __name__ == "__main__":
    app.run()
""")
    
    (test_dir / "models.py").write_text("""
class User:
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
""")
    
    (test_dir / "utils.py").write_text("""
def helper_function():
    return "helper"
""")
    
    (test_dir / "README.md").write_text("""
# Test Project
This is a test project for validation.
""")
    
    (test_dir / ".env").write_text("""
DEBUG=true
DATABASE_URL=sqlite:///test.db
""")
    
    return test_dir

def validate_cli_commands():
    """Validate CLI commands work correctly"""
    tests = []
    
    # Test 1: CLI help
    success, output = run_command("projectprompt --help", "CLI help command")
    tests.append(("CLI Help", success, "Commands should be available" if success else output))
    
    # Test 2: Version
    success, output = run_command("projectprompt --version", "CLI version command")
    tests.append(("CLI Version", success, "Version 2.0.0 expected" if success else output))
    
    return tests

def validate_analysis_workflow():
    """Validate the complete analysis workflow"""
    tests = []
    
    # Create test project
    test_dir = create_test_project()
    original_dir = os.getcwd()
    
    try:
        # Test 3: Analyze command
        os.chdir(test_dir)
        success, output = run_command("projectprompt analyze .", "Project analysis")
        tests.append(("Analysis Command", success, "Should analyze project without API keys" if success else output))
        
        # Test 4: Status command
        success, output = run_command("projectprompt status", "Status command")
        tests.append(("Status Command", success, "Should show project status" if success else output))
        
        # Test 5: Check if analysis.json was created
        analysis_file = test_dir / "analysis.json"
        if analysis_file.exists():
            tests.append(("Analysis File Created", True, "analysis.json exists"))
            try:
                with open(analysis_file) as f:
                    data = json.load(f)
                tests.append(("Analysis JSON Valid", True, "Valid JSON structure"))
            except Exception as e:
                tests.append(("Analysis JSON Valid", False, f"JSON error: {e}"))
        else:
            tests.append(("Analysis File Created", False, "analysis.json not found"))
            tests.append(("Analysis JSON Valid", False, "No file to validate"))
        
        # Test 6: Suggest command (should fail without API key)
        success, output = run_command("projectprompt suggest \"test_group\"", "Suggest command without API", check_returncode=False)
        api_key_check = "API key not found" in output or "No API key" in output
        tests.append(("API Key Validation", api_key_check, "Should require API key for suggestions" if api_key_check else f"API validation not working: {output}"))
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)
    
    return tests

def validate_configuration():
    """Validate configuration system"""
    tests = []
    
    # Test 7: Config class import
    try:
        from src_new.utils.config import Config
        config = Config()
        tests.append(("Config Import", True, "Configuration class accessible"))
        
        # Test 8: API key validation methods
        has_anthropic = hasattr(config, 'has_anthropic_key')
        has_openai = hasattr(config, 'has_openai_key')
        has_any = hasattr(config, 'has_any_api_key')
        all_methods = has_anthropic and has_openai and has_any
        tests.append(("API Key Methods", all_methods, "All API key validation methods present" if all_methods else "Missing API key methods"))
        
    except Exception as e:
        tests.append(("Config Import", False, f"Import failed: {e}"))
        tests.append(("API Key Methods", False, "Cannot test due to import failure"))
    
    return tests

def main():
    """Run all validation tests"""
    print("🚀 Phase 4 CLI Validation Starting...")
    print("=" * 50)
    
    all_tests = []
    
    # Run validation suites
    all_tests.extend(validate_cli_commands())
    all_tests.extend(validate_analysis_workflow())
    all_tests.extend(validate_configuration())
    
    # Summary
    passed = sum(1 for _, success, _ in all_tests if success)
    total = len(all_tests)
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    for test_name, success, message in all_tests:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
    
    if passed == total:
        print("\n🎉 Phase 4 CLI implementation is complete and working!")
        return 0
    else:
        print(f"\n⚠️  Phase 4 has {total - passed} issues to resolve")
        return 1

if __name__ == "__main__":
    sys.exit(main())
