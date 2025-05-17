#!/usr/bin/env python
"""
Test script for the implementation prompt generator.

This script tests the implementation prompt generator directly,
bypassing the CLI interface to verify its functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

# Import directly from implementation_prompt_generator.py
from src.generators.implementation_prompt_generator import ImplementationPromptGenerator

def test_implementation_prompt_generator():
    """Test the implementation prompt generator directly."""
    print("Testing Implementation Prompt Generator")
    print("--------------------------------------")
    
    # Create an instance with premium access
    generator = ImplementationPromptGenerator(is_premium=True)
    
    # Test generating an implementation prompt
    feature = "authentication"
    result = generator.generate_implementation_prompt(
        project_path=project_root,
        feature_name=feature
    )
    
    print(f"Generated prompt for {feature}: {'Success' if result.get('success') else 'Failed'}")
    
    if result.get('success'):
        # Print a preview of the implementation guide
        impl_guide = result.get('implementation_guide', '')
        preview_length = 300
        print(f"\nPreview of implementation guide ({len(impl_guide)} chars):")
        print("--------------------------------------")
        print(impl_guide[:preview_length] + "..." if len(impl_guide) > preview_length else impl_guide)
    else:
        print(f"\nError: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_implementation_prompt_generator()
