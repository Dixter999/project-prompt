#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Get the absolute path of the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to the Python path
sys.path.insert(0, project_root)

# Try to import the module
try:
    from src.generators.implementation_prompt_generator_simple import ImplementationPromptGenerator
    print("Import successful!")
    
    # Try to create an instance
    generator = ImplementationPromptGenerator(is_premium=True)
    print("Class instantiation successful!")
    
    # Try a method
    result = generator.generate_implementation_prompt("test_path", "TestFeature")
    print(f"Method call successful: {result[:30]}...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    
print("Script completed.")
