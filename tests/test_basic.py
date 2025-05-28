#!/usr/bin/env python3
"""
Basic tests for project-prompt package functionality.
"""
import pytest
from pathlib import Path


def test_basic_functionality():
    """Test that basic Python functionality works."""
    assert True
    assert 1 + 1 == 2


def test_project_structure():
    """Test that essential project files exist."""
    project_root = Path(__file__).parent.parent
    
    # Check essential files exist
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "README.md").exists() 
    assert (project_root / "src").exists()
    assert (project_root / "src" / "main.py").exists()
