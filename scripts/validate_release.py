#!/usr/bin/env python3
"""
ProjectPrompt v1.0.0 Release Validation Script
Tests core functionality to ensure the release is ready.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and return success status."""
    print(f"🧪 Testing: {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed with code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("🚀 ProjectPrompt v1.0.0 Release Validation")
    print("=" * 60)
    
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("python3 -c 'import src; print(\"Import src successful\")'", "Import src module"),
        ("python3 -c 'import src.main; print(\"Import main successful\")'", "Import main module"),
        ("python3 -c 'from src.utils.config import config_manager; print(\"Config manager works\")'", "Config manager"),
        ("python3 -c 'from src.utils import logger; print(\"Logger works\")'", "Logger functionality"),
        ("pip install -e . --quiet", "Package installation"),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, description in tests:
        if run_command(command, description):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! v1.0.0 is ready for release!")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
