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
        print(f"   ❌ Error: {e}")
        return False, str(e)

def create_test_project():
    """Create a test project for validation"""
    test_dir = Path(tempfile.mkdtemp(prefix="pp_test_"))
    
    # Create test files
    (test_dir / "app.py").write_text("""
def main():
    print("Hello World")
    
if __name__ == "__main__":
    main()
""")
    
    (test_dir / "utils.py").write_text("""
def helper_function():
    return "helper"
""")
    
    (test_dir / "README.md").write_text("""
# Test Project
This is a test project for validation.
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
    
    try:
        # Test 3: Analyze command
        os.chdir(test_dir)
        success, output = run_command("projectprompt analyze .", "Project analysis")
        tests.append(("Analysis Command", success, "Should analyze project without API keys" if success else output))
        
        # Test 4: Check if analysis files were created
        analysis_dir = test_dir / "project-output"
        analysis_file = analysis_dir / "analysis.json"
        success = analysis_file.exists()
        tests.append(("Analysis Files Created", success, "analysis.json should exist" if success else "analysis.json not found"))
        
        # Test 5: Status command
        success, output = run_command("projectprompt status", "Status command")
        tests.append(("Status Command", success, "Should show analysis status" if success else output))
        
        # Test 6: Suggest command (should fail without API key)
        success, output = run_command("projectprompt suggest \"test_group\"", "Suggest command without API", check_returncode=False)
        api_key_check = "API key not found" in output
        tests.append(("API Key Validation", api_key_check, "Should require API key for suggestions" if api_key_check else "API validation not working"))
        
    finally:
        # Cleanup
        os.chdir("/")
        shutil.rmtree(test_dir, ignore_errors=True)
    
    return tests

def validate_configuration():
    """Validate configuration system"""
    tests = []
    
    # Test 7: Config class import
    try:
        from src_new.utils.config import Config
        config = Config()
        success = hasattr(config, 'has_any_api_key')
        tests.append(("Config Import", success, "Config class should be importable" if success else "Config import failed"))
        
        # Test 8: API key checking methods
        success = hasattr(config, 'has_anthropic_key') and hasattr(config, 'has_openai_key')
        tests.append(("API Key Methods", success, "API key check methods should exist" if success else "API key methods missing"))
        
    except Exception as e:
        tests.append(("Config Import", False, f"Import error: {e}"))
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
