"""Tests para la funcionalidad básica."""
import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_version_command():
    """Verificar que el comando version funcione."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ProjectPrompt v0.1.0" in result.stdout

def test_init_command():
    """Verificar que el comando init funcione."""
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Inicializando ProjectPrompt" in result.stdout
    assert "Proyecto inicializado correctamente" in result.stdout

def test_generate_prompts_command():
    """Verificar que el comando generate_prompts funcione."""
    result = runner.invoke(app, ["generate_prompts", "--output", "test_output"])
    assert result.exit_code == 0
    assert "Generando prompts" in result.stdout

def test_generate_prompts_enhanced_command():
    """Verificar que el comando generate_prompts con flag enhanced funcione."""
    result = runner.invoke(app, ["generate_prompts", "--enhanced", "--output", "test_output"])
    assert result.exit_code == 0
    assert "Generando prompts contextuales mejorados" in result.stdout
