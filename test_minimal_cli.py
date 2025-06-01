#!/usr/bin/env python3
"""
Minimal test of CLI imports to debug hanging issue
"""

print("Testing minimal CLI imports...")

try:
    print("1. Testing basic imports...")
    import os
    import sys
    from typing import List, Optional
    print("   ✓ Basic imports OK")
except Exception as e:
    print(f"   ✗ Basic imports failed: {e}")
    exit(1)

try:
    print("2. Testing Rich imports...")
    from rich.console import Console
    from rich.panel import Panel
    print("   ✓ Rich imports OK")
except Exception as e:
    print(f"   ✗ Rich imports failed: {e}")
    exit(1)

try:
    print("3. Testing src version import...")
    from src import __version__
    print(f"   ✓ Version import OK: {__version__}")
except Exception as e:
    print(f"   ✗ Version import failed: {e}")
    exit(1)

try:
    print("4. Testing logger import directly...")
    from src.utils.logger import get_logger
    print("   ✓ Direct logger import OK")
except Exception as e:
    print(f"   ✗ Direct logger import failed: {e}")
    exit(1)

try:
    print("5. Testing utils package import...")
    from src.utils import logger
    print("   ✓ Utils package import OK")
except Exception as e:
    print(f"   ✗ Utils package import failed: {e}")
    exit(1)

print("All tests completed!")
