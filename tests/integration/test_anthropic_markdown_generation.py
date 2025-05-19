#!/usr/bin/env python3
"""
Comprehensive Test Script for Anthropic Markdown Generation

This script runs a series of tests to validate that the Anthropic API integration
is working correctly and generating appropriate markdown content based on different
project types.

Tests:
1. API Key Validation
2. Basic API Connection Test
3. Project Analysis Test with Simple Project
4. Project Analysis Test with Complex Project
5. Template Application Test
6. Content Quality Evaluation

Usage:
    python test_anthropic_markdown_generation.py [--api-key YOUR_API_KEY]
"""

import os
import sys
import argparse
import json
import re
import tempfile
import time
import shutil
from pathlib import Path
import subprocess

# Terminal colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

def print_section(title):
    """Print a section title with formatting."""
    print(f"\n{BOLD}{UNDERLINE}{title}{NC}\n")

def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✓ {message}{NC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}! {message}{NC}")

def print_error(message):
    """Print an error message."""
    print(f"{RED}✗ {message}{NC}")

def validate_api_key(api_key):
    """Validate the Anthropic API key format."""
    if not api_key:
        print_error("API key is empty")
        return False
    
    # Basic format validation (this is just a simple check)
    if not api_key.startswith("sk-"):
        print_warning("API key doesn't start with 'sk-' which is unusual for Anthropic keys")
    
    if len(api_key) < 20:
        print_error("API key is too short to be valid")
        return False
    
    print_success(f"API key format looks valid: {api_key[:4]}...{api_key[-4:]}")
    return True

def test_api_connection(api_key):
    """Test the connection to Anthropic API with a simple request."""
    try:
        import requests
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 30,
            "messages": [{"role": "user", "content": "Reply with 'API connection successful' in markdown format"}]
        }
        
        print("Making test API request to Anthropic...")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print_error(f"API request failed with status code: {response.status_code}")
            print(f"Error details: {response.text}")
            return False
        
        result = response.json()
        content = result.get("content", [])
        
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        
        response_text = "".join(text_parts).strip()
        print(f"API Response: {response_text}")
        
        if "API connection successful" in response_text:
            print_success("API connection test passed")
            return True
        else:
            print_warning("API connection worked but response content was unexpected")
            return True  # Still return True since the API connection itself worked
        
    except Exception as e:
        print_error(f"Error testing API connection: {e}")
        return False

def create_test_project(type_name="simple"):
    """Create a simple test project structure for analysis."""
    # Create project directory inside test-projects folder
    base_dir = "/mnt/h/Projects/project-prompt/test-projects"
    project_dir = os.path.join(base_dir, f"anthropic_test_project_{type_name}")
    
    # Create directory if it doesn't exist
    os.makedirs(project_dir, exist_ok=True)
    
    if type_name == "simple":
        # Create a simple Python project
        files = {
            "main.py": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()",
            "utils.py": "def helper():\n    return 'Helper function'",
            "README.md": "# Test Project\n\nA simple test project for testing Anthropic markdown generation.",
            "requirements.txt": "requests==2.28.1\npython-dotenv==0.21.0"
        }
    elif type_name == "api":
        # Create an API project
        files = {
            "app.py": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'API Home'\n\n@app.route('/api/data')\ndef get_data():\n    return {'data': 'example'}\n\nif __name__ == '__main__':\n    app.run(debug=True)",
            "models.py": "class User:\n    def __init__(self, name, email):\n        self.name = name\n        self.email = email",
            "routes.py": "# API Routes\ndef register_routes(app):\n    # User routes\n    app.add_url_rule('/api/users', view_func=get_users)\n    app.add_url_rule('/api/users/<id>', view_func=get_user)\n\ndef get_users():\n    return 'All users'\n\ndef get_user(id):\n    return f'User {id}'",
            "README.md": "# API Project\n\nA test API project for testing Anthropic markdown generation.",
            "requirements.txt": "flask==2.2.2\nrequests==2.28.1"
        }
    elif type_name == "frontend":
        # Create a frontend project
        files = {
            "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Test Frontend</title>\n    <link rel='stylesheet' href='styles.css'>\n</head>\n<body>\n    <div id='app'></div>\n    <script src='main.js'></script>\n</body>\n</html>",
            "styles.css": "body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}\n\n#app {\n    max-width: 800px;\n    margin: 0 auto;\n}",
            "main.js": "document.addEventListener('DOMContentLoaded', () => {\n    const app = document.getElementById('app');\n    app.innerHTML = '<h1>Hello World</h1>';\n\n    // Example component\n    function createButton(text, onClick) {\n        const button = document.createElement('button');\n        button.textContent = text;\n        button.addEventListener('click', onClick);\n        return button;\n    }\n\n    const btn = createButton('Click me', () => alert('Button clicked!'));\n    app.appendChild(btn);\n});",
            "README.md": "# Frontend Project\n\nA test frontend project for testing Anthropic markdown generation."
        }
    elif type_name == "cli":
        # Create a CLI project
        files = {
            "cli.py": "#!/usr/bin/env python3\nimport argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description='Test CLI')\n    parser.add_argument('command', choices=['run', 'test', 'help'], help='Command to execute')\n    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')\n    \n    args = parser.parse_args()\n    \n    if args.command == 'run':\n        run_command(args.verbose)\n    elif args.command == 'test':\n        test_command(args.verbose)\n    elif args.command == 'help':\n        parser.print_help()\n\ndef run_command(verbose):\n    print('Running command')\n    if verbose:\n        print('With verbose output')\n\ndef test_command(verbose):\n    print('Testing command')\n    if verbose:\n        print('With verbose output')\n\nif __name__ == '__main__':\n    main()",
            "commands/__init__.py": "",
            "commands/run.py": "def execute(verbose=False):\n    print('Executing run command')",
            "commands/test.py": "def execute(verbose=False):\n    print('Executing test command')",
            "README.md": "# CLI Project\n\nA test CLI project for testing Anthropic markdown generation.\n\n## Usage\n\n```\npython cli.py [command] [options]\n```"
        }
    
    # Create the files
    for filename, content in files.items():
        # Create directories if needed
        filepath = os.path.join(project_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)
    
    print_success(f"Created test project of type '{type_name}' at: {project_dir}")
    return project_dir

def run_analysis_with_anthropic(project_path, api_key, output_file):
    """Run project analysis with Anthropic API and save the output."""
    # Ensure output file is in test-projects directory
    if not output_file.startswith("/mnt/h/Projects/project-prompt/test-projects/"):
        output_file = os.path.join("/mnt/h/Projects/project-prompt/test-projects", os.path.basename(output_file))
    
    # Create a temporary environment file with the API key
    env_file = os.path.join("/mnt/h/Projects/project-prompt/test-projects", '.env.test')
    with open(env_file, 'w') as f:
        f.write(f"anthropic_API={api_key}\n")
    
    try:
        # Run the analyzer script with the test environment
        analyzer_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analyze_with_anthropic_direct.py')
        
        env = os.environ.copy()
        env['anthropic_API'] = api_key
        
        cmd = [sys.executable, analyzer_script, project_path, '--output', output_file]
        print(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print_error(f"Analysis failed with exit code: {process.returncode}")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        if not os.path.exists(output_file):
            print_error(f"Output file was not created: {output_file}")
            return False
        
        print_success(f"Analysis completed and saved to: {output_file}")
        return True
    
    finally:
        # Cleanup
        if os.path.exists(env_file):
            os.remove(env_file)

def analyze_markdown_quality(markdown_file):
    """Analyze the quality of the generated markdown."""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content or len(content) < 100:
            print_error(f"Output file is empty or too short: {len(content)} chars")
            return False
        
        # Look for Anthropic-generated content
        if "Sugerencias de Mejora (Generado por Anthropic Claude)" not in content:
            print_error("No Anthropic-generated content found")
            return False
        
        # Count sections
        headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
        print(f"Document has {len(headings)} headings:")
        for heading in headings[:5]:  # Show first 5 headings
            print(f"  - {heading}")
        if len(headings) > 5:
            print(f"  - ... and {len(headings) - 5} more")
        
        # Count code blocks
        code_blocks = re.findall(r'```[\w]*\n[\s\S]*?\n```', content)
        print(f"Document has {len(code_blocks)} code blocks")
        
        # Check for lists
        lists = re.findall(r'^\s*[*-]\s+.+$', content, re.MULTILINE)
        print(f"Document has {len(lists)} list items")
        
        # Word count as a quality metric
        words = len(content.split())
        print(f"Document word count: {words}")
        
        quality_score = 0
        
        # Scoring based on content richness
        if len(headings) >= 5:
            quality_score += 1
        if len(code_blocks) >= 1:
            quality_score += 1
        if len(lists) >= 5:
            quality_score += 1
        if words >= 300:
            quality_score += 1
        
        # Check if important sections are present
        important_sections = [
            r"(Resumen|Propósito|Estructura)",
            r"(Fortalezas|Puntos Fuertes)",
            r"(Debilidades|Áreas de Mejora)",
            r"(Recomendaciones|Sugerencias)"
        ]
        
        section_score = 0
        for pattern in important_sections:
            if re.search(r'#+\s+' + pattern, content, re.IGNORECASE):
                section_score += 1
        
        quality_score += section_score
        
        max_score = 8  # Maximum possible score
        quality_percentage = (quality_score / max_score) * 100
        
        print(f"Quality score: {quality_score}/{max_score} ({quality_percentage:.1f}%)")
        
        if quality_score >= 6:
            print_success("Markdown quality is good")
        elif quality_score >= 4:
            print_warning("Markdown quality is acceptable but could be improved")
        else:
            print_error("Markdown quality is poor")
            return False
        
        return True
    
    except Exception as e:
        print_error(f"Error analyzing markdown: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test Anthropic markdown generation')
    parser.add_argument('--api-key', help='Anthropic API key to use for testing')
    parser.add_argument('--skip-project-creation', action='store_true', 
                        help='Skip test project creation and use existing project')
    parser.add_argument('--project-path', help='Path to existing project to analyze (used with --skip-project-creation)')
    args = parser.parse_args()
    
    print_section("ANTHROPIC MARKDOWN GENERATION TEST")
    
    # Step 1: Get and validate API key
    api_key = args.api_key
    if not api_key:
        # Try to get from environment
        api_key = os.getenv("anthropic_API")
        
        # Try to get from .env file
        if not api_key:
            env_paths = ['.env', '.env.local', '.env.test']
            for env_path in env_paths:
                try:
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            for line in f:
                                if line.startswith('anthropic_API'):
                                    api_key = line.split('=')[1].strip().strip('"\'')
                                    break
                        if api_key:
                            break
                except Exception:
                    continue
    
    if not api_key:
        print_error("No API key found. Please provide one with --api-key or set anthropic_API environment variable")
        sys.exit(1)
    
    print_section("1. API KEY VALIDATION")
    if not validate_api_key(api_key):
        sys.exit(1)
    
    print_section("2. API CONNECTION TEST")
    if not test_api_connection(api_key):
        sys.exit(1)
    
    # Step 3: Create and analyze projects
    project_types = ["simple", "api", "frontend", "cli"]
    test_results = {}
    
    if args.skip_project_creation:
        if not args.project_path:
            print_error("--project-path must be provided when using --skip-project-creation")
            sys.exit(1)
            
        if not os.path.isdir(args.project_path):
            print_error(f"Project path does not exist: {args.project_path}")
            sys.exit(1)
            
        print_section(f"3. ANALYZING EXISTING PROJECT")
        print(f"Project path: {args.project_path}")
        
        output_file = f"/mnt/h/Projects/project-prompt/test-projects/anthropic_analysis_existing.md"
        
        if run_analysis_with_anthropic(args.project_path, api_key, output_file):
            print_section("4. CONTENT QUALITY EVALUATION")
            analyze_markdown_quality(output_file)
            
    else:
        for i, project_type in enumerate(project_types):
            print_section(f"3.{i+1}. {project_type.upper()} PROJECT TEST")
            
            # Create test project
            project_dir = create_test_project(project_type)
            
            # Run analysis
            output_file = f"/mnt/h/Projects/project-prompt/test-projects/anthropic_analysis_{project_type}.md"
            
            if run_analysis_with_anthropic(project_dir, api_key, output_file):
                print_section(f"4.{i+1}. CONTENT QUALITY EVALUATION ({project_type.upper()})")
                success = analyze_markdown_quality(output_file)
                test_results[project_type] = success
            else:
                test_results[project_type] = False
            
            # Small delay to avoid API rate limits
            if i < len(project_types) - 1:
                print("Waiting before next test...")
                time.sleep(2)
    
    # Print summary
    print_section("TEST SUMMARY")
    
    if args.skip_project_creation:
        output_file = "/mnt/h/Projects/project-prompt/test-projects/anthropic_analysis_existing.md"
        if os.path.exists(output_file):
            print_success("Existing project analysis completed successfully")
            print(f"Output file: {output_file}")
        else:
            print_error("Existing project analysis failed")
    else:
        all_passed = all(test_results.values())
        
        for project_type, success in test_results.items():
            status = f"{GREEN}PASSED{NC}" if success else f"{RED}FAILED{NC}"
            print(f"{project_type.upper()} project test: {status}")
        
        if all_passed:
            print_success("All tests passed! Anthropic markdown generation is working correctly")
        else:
            print_error("Some tests failed. Check the output files for details")

if __name__ == "__main__":
    main()
