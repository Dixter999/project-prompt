#!/usr/bin/env python3
"""Simple status check script."""

import os
import subprocess
import sys
from pathlib import Path

def main():
    print("🔍 ProjectPrompt Status Check")
    print("=" * 40)
    
    # Check current directory
    cwd = Path.cwd()
    print(f"Current directory: {cwd}")
    
    # Check if we're in the right place
    project_root = Path("/mnt/h/Projects/project-prompt")
    if project_root.exists():
        print(f"✅ Project directory exists: {project_root}")
        os.chdir(project_root)
    else:
        print(f"❌ Project directory not found: {project_root}")
        return 1
    
    # Check key files
    key_files = [
        "pyproject.toml",
        "src/main.py", 
        "src/utils/config.py",
        "scripts/validate_release.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Try to import the main module
    try:
        sys.path.insert(0, str(project_root))
        import src.main
        print("✅ Can import src.main")
    except Exception as e:
        print(f"❌ Cannot import src.main: {e}")
    
    # Check git status
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], 
            capture_output=True, 
            text=True, 
            cwd=project_root
        )
        if result.returncode == 0:
            commit = result.stdout.strip()[:8]
            print(f"✅ Git HEAD: {commit}")
        else:
            print(f"❌ Git error: {result.stderr}")
    except Exception as e:
        print(f"❌ Git command failed: {e}")
    
    # Test CLI installation
    try:
        result = subprocess.run(
            ["pip", "install", "-e", "."], 
            capture_output=True, 
            text=True, 
            cwd=project_root
        )
        if result.returncode == 0:
            print("✅ Package installation successful")
        else:
            print(f"❌ Package installation failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"❌ Installation error: {e}")

if __name__ == "__main__":
    main()
