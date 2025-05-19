"""Tests para ProjectPrompt."""
import pytest
from src import __version__

def test_version():
    """Verificar que la versión sea correcta."""
    assert __version__ == "0.1.0"
