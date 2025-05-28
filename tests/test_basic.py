#!/usr/bin/env python3
"""
Basic tests for project-prompt package functionality.
"""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that main modules can be imported without errors."""
    try:
        import src.main
        import src.utils.logger
        import src.utils.config_manager
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_config_manager():
    """Test basic config manager functionality."""
    from src.utils.config_manager import get_config_manager
    
    config_manager = get_config_manager()
    assert config_manager is not None
    
    # Test getting a default value
    value = config_manager.get("non_existent_key", "default_value")
    assert value == "default_value"


def test_logger():
    """Test logger functionality."""
    from src.utils.logger import get_logger
    
    logger = get_logger()
    assert logger is not None
    
    # Test basic logging operations don't crash
    logger.info("Test log message")
    logger.debug("Test debug message")


def test_project_structure():
    """Test that essential project files exist."""
    project_root = Path(__file__).parent.parent
    
    # Check essential files exist
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "src").exists()
    assert (project_root / "src" / "main.py").exists()
