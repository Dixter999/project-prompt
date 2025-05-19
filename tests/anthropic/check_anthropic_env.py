#!/usr/bin/env python3
"""
Check if the environment is properly configured for Anthropic testing.
This script verifies:
1. API key is available
2. Required dependencies are installed
3. Output directory is writable
"""

import os
import sys
import importlib

# Terminal colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color
BOLD = "\033[1m"

def check_api_key():
    """Verify that Anthropic API key is configured."""
    api_key = os.environ.get("anthropic_API")
    
    # Search in .env files
    if not api_key:
        env_files = [
            ".env",
            "test-projects/.env",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        ]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('anthropic_API'):
                                parts = line.split('=', 1)
                                if len(parts) == 2:
                                    api_key = parts[1].strip().strip('"\'')
                                    break
                except Exception:
                    pass
            
            if api_key:
                break
    
    if not api_key:
        print(f"{RED}✗ Anthropic API key not found{NC}")
        print(f"{YELLOW}Please configure it in one of these ways:{NC}")
        print("  - Create .env file with anthropic_API=your_key")
        print("  - Export environment variable: export anthropic_API=your_key")
        return False
    
    # Basic validation
    if len(api_key) < 20:
        print(f"{RED}✗ API key found but seems too short to be valid{NC}")
        return False
        
    print(f"{GREEN}✓ Anthropic API key found{NC}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ["requests", "json", "pathlib"]
    missing = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"{RED}✗ Missing dependencies: {', '.join(missing)}{NC}")
        return False
        
    print(f"{GREEN}✓ All required dependencies are installed{NC}")
    return True

def check_output_directory():
    """Check if output directory is writable."""
    output_dir = "/mnt/h/Projects/project-prompt/test-projects"
    
    # Check if directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"{GREEN}✓ Output directory created: {output_dir}{NC}")
        except Exception as e:
            print(f"{RED}✗ Cannot create output directory: {e}{NC}")
            return False
    
    # Check if directory is writable
    test_file = os.path.join(output_dir, ".write_test")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"{GREEN}✓ Output directory is writable{NC}")
        return True
    except Exception as e:
        print(f"{RED}✗ Output directory is not writable: {e}{NC}")
        return False

def check_analyzer_scripts():
    """Check if analyzer scripts exist."""
    scripts = [
        "/mnt/h/Projects/project-prompt/analyze_with_anthropic_direct.py",
        "/mnt/h/Projects/project-prompt/project_analyzer.py"
    ]
    
    missing = []
    for script in scripts:
        if not os.path.exists(script):
            missing.append(script)
    
    if missing:
        print(f"{RED}✗ Missing required scripts: {', '.join(missing)}{NC}")
        return False
        
    print(f"{GREEN}✓ All required analyzer scripts found{NC}")
    return True

def main():
    """Main function."""
    print(f"{BOLD}Checking environment for Anthropic testing...{NC}\n")
    
    success = True
    success &= check_api_key()
    success &= check_dependencies()
    success &= check_output_directory()
    success &= check_analyzer_scripts()
    
    print("\n" + "-" * 50)
    if success:
        print(f"{GREEN}{BOLD}✓ Environment is ready for Anthropic testing!{NC}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Environment is not correctly set up.{NC}")
        print(f"{YELLOW}Please address the issues above before running tests.{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
