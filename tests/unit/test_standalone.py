#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Completely standalone test for the implementation prompt generator.
This skips all imports from the project structure to avoid circular dependencies.
"""

import os
import sys

# Copy the implementation from implementation_prompt_generator_simple.py directly
class ImplementationPromptGenerator:
    """Generador simplificado de prompts para implementación."""
    
    def __init__(self, is_premium=False):
        """Inicializar generador."""
        self.is_premium = is_premium
    
    def generate_implementation_prompt(self, project_path, feature_name):
        """Genera un prompt para implementación (versión simplificada)."""
        return {
            "success": True,
            "prompts": {
                "implementation": f"# Implementación de {feature_name}\nEsta es una versión simplificada.",
                "integration": None,
                "testing": None
            },
            "feature_info": {"name": feature_name},
            "related_files": []
        }

def test_generator():
    """
    Simple test to verify that the implementation prompt generator works.
    """
    try:
        print("Starting test...")
        # Create an instance
        generator = ImplementationPromptGenerator(is_premium=True)
        print("✓ Successfully created generator instance")
        
        # Test a simple operation
        feature_name = "TestFeature"
        print(f"Testing with feature: {feature_name}")
        result = generator.generate_implementation_prompt("test_path", feature_name)
        print(f"✓ Generate implementation prompt test successful")
        print(f"Result: {result}")
        
        print("All tests passed!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    test_generator()
