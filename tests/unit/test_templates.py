#!/usr/bin/env python3
"""
Test script to check if our template files are valid.
"""
import os
import sys

# Get the template path
templates_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    "src", "templates", "tests"
)

print(f"Looking for templates in: {templates_dir}")

def read_template(template_name):
    """Read a template file."""
    template_path = os.path.join(templates_dir, f"{template_name}.py")
    if not os.path.exists(template_path):
        print(f"Template file not found: {template_path}")
        return None
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

# Try to read the templates
try:
    class_template = read_template("class_test")
    module_template = read_template("module_test")
    print("Templates loaded successfully!")
    
    # Test replacements
    replacements = {
        "{{module_name}}": "test_module",
        "{{class_name}}": "TestClass",
        "{{module_path}}": "import test_module",
        "{{functions}}": "'test_func1', 'test_func2'",
        "{{test_cases}}": "def test_custom():\n    assert True",
    }
    
    # Apply replacements to class template
    for marker, value in replacements.items():
        class_template = class_template.replace(marker, value)
    
    # Apply replacements to module template
    for marker, value in replacements.items():
        module_template = module_template.replace(marker, value)
    
    print("Replacements applied successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("Template test completed successfully!")
