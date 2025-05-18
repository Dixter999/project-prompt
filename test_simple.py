#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script for checking the implementation prompt generator.
This script directly imports the generator without going through the package system.
"""

import sys
import os

# Get the absolute path of the project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Direct import of the class, avoiding the circular import
from src.generators.implementation_prompt_generator_simple import ImplementationPromptGenerator

def test_simple():
    """
    Simple test to verify that the implementation prompt generator works.
    """
    try:
        # Create an instance
        generator = ImplementationPromptGenerator(is_premium=True)
        print("✓ Successfully created generator instance")
        
        # Test a simple operation
        feature_name = "TestFeature"
        result = generator.generate_implementation_prompt("test_path", feature_name)
        print(f"✓ Generate implementation prompt test successful")
        print(f"Result: {result}")
        
        print("All tests passed!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    test_simple()
