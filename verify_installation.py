#!/usr/bin/env python3
"""
ProjectPrompt User Verification Script

This script verifies that ProjectPrompt is properly installed and configured
for end users. It performs basic functionality checks without requiring
the full development test suite.
"""

import os
import sys
import tempfile
from pathlib import Path

def check_installation():
    """Verify ProjectPrompt installation."""
    print("🔍 Checking ProjectPrompt installation...")
    
    try:
        # Check if we can import the main module
        import src
        print(f"✅ ProjectPrompt v{src.__version__} is installed")
        return True
    except ImportError as e:
        print(f"❌ ProjectPrompt is not properly installed: {e}")
        return False

def check_configuration():
    """Verify configuration system works."""
    print("\n🔧 Checking configuration system...")
    
    try:
        from src.utils.config import ConfigManager
        
        # Test with temporary config
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.yaml")
            config_manager = ConfigManager(config_path=config_path)
            
            # Test basic operations
            config_manager.set("test.key", "test_value")
            value = config_manager.get("test.key")
            
            if value == "test_value":
                print("✅ Configuration system working")
                return True
            else:
                print("❌ Configuration system failed")
                return False
                
    except Exception as e:
        print(f"❌ Configuration system error: {e}")
        return False

def check_core_commands():
    """Verify core commands work."""
    print("\n⚡ Checking core commands...")
    
    try:
        # Test version command
        import subprocess
        result = subprocess.run([sys.executable, "-m", "src.main", "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Core commands working")
            return True
        else:
            print(f"❌ Core commands failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Core commands error: {e}")
        return False

def check_api_configuration():
    """Check if API keys can be configured."""
    print("\n🔑 Checking API configuration...")
    
    try:
        from src.utils.api_validator import get_api_validator
        validator = get_api_validator()
        
        # Just check if the validator can be created
        print("✅ API configuration system available")
        print("💡 Set your API keys using: projectprompt check-env")
        return True
        
    except Exception as e:
        print(f"❌ API configuration error: {e}")
        return False

def main():
    """Run all user verification checks."""
    print("=" * 60)
    print("🚀 ProjectPrompt User Verification")
    print("=" * 60)
    
    checks = [
        ("Installation", check_installation),
        ("Configuration", check_configuration), 
        ("Core Commands", check_core_commands),
        ("API Configuration", check_api_configuration)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ProjectPrompt is ready to use!")
        print("\n📚 Get started with:")
        print("   projectprompt --help")
        print("   projectprompt check-env")
        return 0
    else:
        print("⚠️  Some checks failed. Please check your installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
