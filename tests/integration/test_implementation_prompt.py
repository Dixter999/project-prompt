#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for checking the implementation prompt generator.
"""

from src.generators.implementation_prompt_generator_simple import get_implementation_prompt_generator

def test_generator():
    """
    Simple test to verify that the implementation prompt generator works.
    """
    try:
        # Create an instance
        generator = get_implementation_prompt_generator(is_premium=True)
        print("✓ Successfully created generator instance")
        
        # Test the generate_implementation_prompt method
        feature_name = "TestFeature"
        result = generator.generate_implementation_prompt("test_path", feature_name)
        print(f"✓ Generate implementation prompt test: {result['success']}")
        
        print("All tests passed!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    test_generator()
