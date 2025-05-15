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
