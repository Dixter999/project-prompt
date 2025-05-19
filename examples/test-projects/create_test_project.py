#!/usr/bin/env python3
"""
Project Template Generator for Anthropic Testing

This script creates different types of test projects for verifying Anthropic's
markdown generation capabilities. It copies template projects and customizes them
as needed for comprehensive testing.
"""

import os
import sys
import shutil
import random
import string
import json
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "test-projects")

# Available project types
PROJECT_TYPES = [
    "web-project",
    "backend-api",
    "mobile-app",
    "data-science",
    "cli-tool",   # Will create a simple CLI tool
    "library",    # Will create a simple library project
    "game-dev",   # Will create a game development project
    "mixed"       # Will create a project with multiple components
]

def generate_random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def ensure_dir_exists(path):
    """Ensure directory exists, create if it doesn't"""
    os.makedirs(path, exist_ok=True)
    return path

def copy_template(template_name, output_name):
    """
    Copy template project to output directory
    
    Args:
        template_name (str): Name of the template
        output_name (str): Name for the output project
    
    Returns:
        str: Path to the created project
    """
    source_dir = os.path.join(TEMPLATES_DIR, template_name)
    target_dir = os.path.join(OUTPUT_DIR, output_name)
    
    # Check if template exists
    if not os.path.exists(source_dir):
        logger.error(f"Template '{template_name}' not found in {TEMPLATES_DIR}")
        return None
    
    # Create target directory
    ensure_dir_exists(target_dir)
    
    # Copy template files
    try:
        for item in os.listdir(source_dir):
            source_item = os.path.join(source_dir, item)
            target_item = os.path.join(target_dir, item)
            
            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy2(source_item, target_item)
        
        logger.info(f"Created project from template '{template_name}' at {target_dir}")
        return target_dir
    except Exception as e:
        logger.error(f"Failed to copy template: {e}")
        return None

def customize_project(project_path, project_name, project_type):
    """
    Customize the project with specific name and details
    
    Args:
        project_path (str): Path to the project
        project_name (str): Name for the project
        project_type (str): Type of the project
    """
    try:
        # Update README.md
        readme_path = os.path.join(project_path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Replace template title with project name
            content = content.replace("# Test Project", f"# {project_name}")
            content = content.replace("Test Project", project_name)
            
            with open(readme_path, 'w') as f:
                f.write(content)
        
        # Update package.json for JS/TS projects
        package_path = os.path.join(project_path, "package.json")
        if os.path.exists(package_path):
            with open(package_path, 'r') as f:
                package_data = json.load(f)
            
            package_data["name"] = project_name.lower().replace(" ", "-")
            
            with open(package_path, 'w') as f:
                json.dump(package_data, f, indent=2)
        
        logger.info(f"Customized project '{project_name}' at {project_path}")
    except Exception as e:
        logger.error(f"Failed to customize project: {e}")

def create_test_project(project_type, project_name=None):
    """
    Create a test project of the specified type
    
    Args:
        project_type (str): Type of project to create
        project_name (str, optional): Name for the project
        
    Returns:
        str: Path to the created project
    """
    if project_type not in PROJECT_TYPES:
        logger.error(f"Unknown project type: {project_type}")
        logger.info(f"Available types: {', '.join(PROJECT_TYPES)}")
        return None
    
    # Generate project name if not provided
    if not project_name:
        random_suffix = generate_random_string(6)
        project_name = f"Test {project_type.capitalize()} {random_suffix}"
    
    # Create project directory name
    dir_name = project_name.lower().replace(" ", "-")
    
    if project_type == "mixed":
        # Create a project with multiple components
        return create_mixed_project(dir_name, project_name)
    else:
        # Create a single type project
        return copy_and_customize(project_type, dir_name, project_name)

def copy_and_customize(project_type, dir_name, project_name):
    """Copy template and customize it"""
    project_path = copy_template(project_type, dir_name)
    if project_path:
        customize_project(project_path, project_name, project_type)
        return project_path
    return None

def create_mixed_project(dir_name, project_name):
    """
    Create a mixed project with multiple components
    
    Args:
        dir_name (str): Directory name for the project
        project_name (str): Name for the project
        
    Returns:
        str: Path to the created project
    """
    # Create the main project directory
    project_path = os.path.join(OUTPUT_DIR, dir_name)
    ensure_dir_exists(project_path)
    
    # Create README.md
    with open(os.path.join(project_path, "README.md"), 'w') as f:
        f.write(f"# {project_name}\n\n"
                f"A multi-component project for testing Anthropic markdown generation.\n\n"
                f"## Components\n\n"
                f"- Frontend: Web interface\n"
                f"- Backend: API server\n"
                f"- Mobile: React Native app\n"
                f"- Analysis: Data processing scripts\n")
    
    # Create component directories and copy templates
    components = {
        "frontend": "web-project",
        "backend": "backend-api",
        "mobile": "mobile-app",
        "analysis": "data-science"
    }
    
    for component_name, template_name in components.items():
        component_path = os.path.join(project_path, component_name)
        ensure_dir_exists(component_path)
        
        # Copy template contents to component directory
        source_dir = os.path.join(TEMPLATES_DIR, template_name)
        if os.path.exists(source_dir):
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(component_path, item)
                
                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, target_item)
    
    logger.info(f"Created mixed project '{project_name}' at {project_path}")
    return project_path

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Create test projects for Anthropic markdown generation testing')
    parser.add_argument('--type', choices=PROJECT_TYPES, default='web-project',
                        help='Type of project to create')
    parser.add_argument('--name', help='Name for the project')
    parser.add_argument('--output-dir', help='Output directory for the project')
    
    args = parser.parse_args()
    
    # Set output directory if provided
    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = os.path.abspath(args.output_dir)
    
    # Create project
    project_path = create_test_project(args.type, args.name)
    
    if project_path:
        print(f"Project created successfully at: {project_path}")
    else:
        print("Failed to create project")
        sys.exit(1)

if __name__ == "__main__":
    main()
