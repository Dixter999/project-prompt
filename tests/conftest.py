import os
import pytest
from pathlib import Path
from typing import Generator

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before any tests run."""
    # Create project-output directory if it doesn't exist
    output_dir = Path("project-output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a minimal README if it doesn't exist
    readme = output_dir / "README.md"
    if not readme.exists():
        readme.write_text("# Project Output\n\nGenerated documentation will appear here.")

@pytest.fixture
def project_output_dir() -> Path:
    """Fixture that provides the project output directory path."""
    output_dir = Path("project-output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture
def test_data_dir() -> Path:
    """Fixture that provides the test data directory path."""
    test_dir = Path(__file__).parent / "data"
    test_dir.mkdir(exist_ok=True)
    return test_dir
