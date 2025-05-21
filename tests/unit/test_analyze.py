#!/usr/bin/env python3
"""
Test for the analyze function in the main module.
"""
import os
import pytest
from src.main import analyze

def test_analyze():
    """
    Test that the analyze function runs without errors.
    """
    # Use a known test directory for consistent results
    test_path = os.path.dirname(os.path.abspath(__file__))
    
    # This test just verifies that the function runs without raising exceptions
    analyze(path=test_path)
    
    # If we get here without exceptions, the test passes
    assert True
