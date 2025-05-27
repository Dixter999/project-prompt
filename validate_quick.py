#!/usr/bin/env python3
"""
Quick validation test for ProjectPrompt v1.0.0
Tests core functionality without terminal complexity
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing module imports...")
    
    # Add project to path
    project_root = Path("/mnt/h/Projects/project-prompt")
    sys.path.insert(0, str(project_root))
    
    try:
        # Test core imports
        import src
        print("✅ Import src: Success")
        
        import src.main
        print("✅ Import src.main: Success")
        
        from src.utils.config import config_manager
        print("✅ Import config_manager: Success")
        
        from src.utils.logger import logger
        print("✅ Import logger: Success")
        
        # Test CLI app import
        from src.main import app
        print("✅ Import CLI app: Success")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_version():
    """Test version information."""
    print("\n📋 Testing version info...")
    
    try:
        # Read pyproject.toml version
        with open("/mnt/h/Projects/project-prompt/pyproject.toml", 'r') as f:
            content = f.read()
            if 'version = "1.0.0"' in content:
                print("✅ Version 1.0.0 confirmed in pyproject.toml")
            else:
                print("❌ Version mismatch in pyproject.toml")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False

def test_files():
    """Test that critical files exist."""
    print("\n📁 Testing critical files...")
    
    project_root = Path("/mnt/h/Projects/project-prompt")
    critical_files = [
        "pyproject.toml",
        "README.md", 
        "CHANGELOG.md",
        "src/main.py",
        "src/utils/config.py",
        "src/utils/logger.py"
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
            
    return all_exist

def main():
    print("🚀 ProjectPrompt v1.0.0 Quick Validation")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_files),
        ("Version Check", test_version), 
        ("Module Imports", test_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! v1.0.0 is ready!")
        print("\n🚀 Ready for deployment:")
        print("1. git checkout -B main")
        print("2. git push origin main")
        print("3. git tag v1.0.0 && git push origin v1.0.0")
        print("4. pip install -e . && project-prompt --version")
        return 0
    else:
        print("⚠️  Some tests failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
