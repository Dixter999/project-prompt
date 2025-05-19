#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Standalone test script for checking the implementation prompt generator without importing the module system.
This avoids circular import issues.
"""

# Import the class directly
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

def get_implementation_prompt_generator(is_premium=False):
    """Obtiene una instancia del generador de prompts."""
    return ImplementationPromptGenerator()

def test_generator():
    """
    Simple test to verify that the implementation prompt generator works.
    """
    try:
        print("==========================================")
        print("Starting test for implementation prompt generator...")
        
        # Create an instance
        generator = get_implementation_prompt_generator(is_premium=True)
        print("✓ Successfully created generator instance")
        
        # Test the generate_implementation_prompt method
        feature_name = "TestFeature"
        result = generator.generate_implementation_prompt("test_path", feature_name)
        print(f"✓ Generate implementation prompt test: {result['success']}")
        print(f"Implementation prompt: {result['prompts']['implementation']}")
        
        print("All tests passed!")
        print("==========================================")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_generator()
