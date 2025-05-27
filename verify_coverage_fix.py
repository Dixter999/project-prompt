#!/usr/bin/env python3
"""
Verify that the coverage fix is working correctly.
This script simulates what happens in the CI environment.
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return True if successful."""
    print(f"🧪 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/mnt/h/Projects/project-prompt")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout[-1000:])  # Last 1000 chars to avoid too much output
            
        if result.stderr:
            print("STDERR:")
            print(result.stderr[-500:])   # Last 500 chars
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("🚀 Verifying Coverage Fix")
    print("=" * 50)
    
    # Set up environment
    os.environ['PYTHONPATH'] = "/mnt/h/Projects/project-prompt"
    os.environ['CI'] = 'true'
    
    # Test 1: Import patch_keyring
    success1 = run_command(
        'python -c "import patch_keyring; print(\'✅ Keyring patched successfully\')"',
        "Testing keyring patch import"
    )
    
    # Test 2: Run coverage test
    coverage_cmd = '''python -m pytest tests/test_config.py tests/test_utils/test_config.py \
  --cov=src.utils.config \
  --cov=src.utils.logger \
  --cov-report=xml \
  --cov-report=term-missing \
  --cov-fail-under=45 \
  -v'''
    
    success2 = run_command(coverage_cmd, "Running coverage test")
    
    # Test 3: Check coverage.xml was created
    success3 = run_command('ls -la coverage.xml && head -5 coverage.xml', "Checking coverage.xml file")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Keyring patch: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Coverage test: {'PASS' if success2 else 'FAIL'}")
    print(f"✅ Coverage XML:  {'PASS' if success3 else 'FAIL'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 ALL TESTS PASSED! Coverage fix is working!")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
