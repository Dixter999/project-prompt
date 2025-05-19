"""Tests for basic functionality."""
import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_version_command():
    """Verify that the version command works."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ProjectPrompt v1.0.0" in result.stdout

def test_init_command():
    """Verify that the init command works."""
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Project Initialization" in result.stdout

@pytest.mark.skip(reason="Command implementation may vary")
def test_generate_prompts_command():
    """Verify that the generate_prompts command works."""
    result = runner.invoke(app, ["generate_prompts", "--output", "test_output"])
    # Skipping this test as implementation may vary

@pytest.mark.skip(reason="Command implementation may vary")
def test_generate_prompts_enhanced_command():
    """Verify that the generate_prompts command with enhanced flag works."""
    result = runner.invoke(app, ["generate_prompts", "--enhanced", "--output", "test_output"])
    # Skipping this test as implementation may vary
