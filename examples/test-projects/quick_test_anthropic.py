#!/usr/bin/env python3
"""
Quick test script for verifying Anthropic markdown generation with a simple project.

This script:
1. Creates a simple test project
2. Runs the Anthropic analysis on it
3. Verifies the quality of generated markdown
"""

import os
import sys
import tempfile
import shutil
import subprocess
import time

# Set output directory
OUTPUT_DIR = "/mnt/h/Projects/project-prompt/test-projects"

def create_simple_test_project():
    """Create a very simple test project with basic structure."""
    project_dir = os.path.join(OUTPUT_DIR, f"simple_test_project_{int(time.time())}")
    
    # Create project directory
    os.makedirs(project_dir, exist_ok=True)
    
    # Create some basic files
    files = {
        "main.py": """
def main():
    print("Hello, world!")
    result = calculate(10, 20)
    print(f"Result: {result}")

def calculate(a, b):
    return a + b

if __name__ == "__main__":
    main()
""",
        "utils.py": """
def helper_function(text):
    """Helper function that processes text."""
    return text.upper()

def format_result(value):
    return f"The result is: {value}"
""",
        "README.md": """
# Simple Test Project

A simple Python project for testing Anthropic markdown generation.

## Features
- Basic Python script
- Utility functions
- Command line interface
""",
        "requirements.txt": """
requests==2.28.1
pytest==7.3.1
"""
    }
    
    # Write files
    for filename, content in files.items():
        file_path = os.path.join(project_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
            
    print(f"Created test project at: {project_dir}")
    return project_dir

def run_anthropic_analysis(project_dir):
    """Run Anthropic analysis on the test project."""
    output_file = os.path.join(OUTPUT_DIR, f"quick_test_output_{int(time.time())}.md")
    
    # Get API key from environment
    api_key = os.environ.get("anthropic_API")
    if not api_key:
        try:
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('anthropic_API'):
                            api_key = line.split('=')[1].strip().strip('"\'')
                            break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    if not api_key:
        print("Error: Anthropic API key not found")
        print("Set the 'anthropic_API' environment variable or create a .env file")
        sys.exit(1)
    
    # Run the analysis
    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analyze_with_anthropic_direct.py"),
        project_dir,
        "--output",
        output_file
    ]
    
    # Create temporary env file
    temp_env_file = os.path.join(OUTPUT_DIR, ".env.temp")
    with open(temp_env_file, 'w') as f:
        f.write(f"anthropic_API={api_key}\n")
    
    print(f"Running analysis: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env["anthropic_API"] = api_key
    
    try:
        process = subprocess.run(cmd, env=env)
        
        if process.returncode != 0:
            print("Error: Analysis failed")
            return None
            
        if not os.path.exists(output_file):
            print(f"Error: Output file not created: {output_file}")
            return None
            
        print(f"Analysis completed successfully")
        return output_file
    
    except Exception as e:
        print(f"Error running analysis: {e}")
        return None
    finally:
        # Clean up
        if os.path.exists(temp_env_file):
            os.unlink(temp_env_file)

def main():
    """Main function."""
    print("=== Quick Test for Anthropic Markdown Generation ===")
    
    # Create test project
    print("\n1. Creating test project...")
    project_dir = create_simple_test_project()
    
    # Run analysis
    print("\n2. Running Anthropic analysis...")
    output_file = run_anthropic_analysis(project_dir)
    
    if not output_file:
        print("\nTest failed: Could not generate analysis")
        return 1
    
    # Show results
    print("\n3. Test results:")
    print(f"- Test project: {project_dir}")
    print(f"- Output file: {output_file}")
    
    # Check if markdown has expected content
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Sugerencias de Mejora (Generado por Anthropic Claude)" in content:
            print("\n✅ Success: Anthropic generated content found in output")
            print(f"\nYou can view the full analysis at: {output_file}")
            return 0
        else:
            print("\n❌ Error: No Anthropic generated content found in output")
            return 1
    
    except Exception as e:
        print(f"\n❌ Error reading output file: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
