#!/usr/bin/env python3
"""
Simplified coverage test for CI
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Import patch_keyring to mock keyring
try:
    import patch_keyring
    print("✅ Keyring patched")
except Exception as e:
    print(f"⚠️ Keyring patch warning: {e}")

# Set environment variables
os.environ['CI'] = 'true'
os.environ['GITHUB_ACTIONS'] = 'true'

# Try to import the modules we're testing
try:
    from src.utils.config import ConfigManager
    print("✅ config.py imported successfully")
except Exception as e:
    print(f"❌ Failed to import config.py: {e}")

try:
    from src.utils.logger import Logger
    print("✅ logger.py imported successfully")
except Exception as e:
    print(f"❌ Failed to import logger.py: {e}")

# Now run pytest with coverage
import subprocess

cmd = [
    sys.executable, '-m', 'pytest',
    'tests/test_config.py',
    'tests/test_utils/test_config.py',
    '--cov=src/utils/config.py',
    '--cov=src/utils/logger.py',
    '--cov-report=term',
    '--cov-fail-under=50',
    '-v'
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd)
print(f"Exit code: {result.returncode}")
sys.exit(result.returncode)
