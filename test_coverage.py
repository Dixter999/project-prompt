#!/usr/bin/env python3
"""
Test script to verify coverage configuration works properly
"""

import os
import sys
import subprocess

def test_coverage():
    """Test the coverage configuration"""
    print("🧪 Testing coverage configuration...")
    
    # Set environment
    os.environ['PYTHONPATH'] = os.getcwd()
    os.environ['CI'] = 'true'
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    # Import patch_keyring
    try:
        import patch_keyring
        print("✅ Keyring patched successfully")
    except ImportError:
        print("❌ Failed to import patch_keyring")
        return False
    
    # Run coverage test
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/test_config.py',
        'tests/test_utils/test_config.py', 
        'tests/test_logger.py',
        '--cov=src/utils',
        '--cov-config=.coveragerc',
        '--cov-report=term-missing',
        '--tb=short',
        '-v'
    ]
    
    print(f"🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("📊 Coverage Output:")
    print(result.stdout)
    
    if result.stderr:
        print("⚠️ Stderr:")
        print(result.stderr)
    
    print(f"📈 Exit code: {result.returncode}")
    
    # Check if coverage passed
    if result.returncode == 0:
        print("✅ Coverage test PASSED")
        return True
    else:
        print("❌ Coverage test FAILED")
        return False

if __name__ == "__main__":
    success = test_coverage()
    sys.exit(0 if success else 1)
