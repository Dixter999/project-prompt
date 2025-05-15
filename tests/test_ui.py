#!/usr/bin/env python3
"""
Tests para la interfaz de línea de comandos (CLI).
"""
import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from typer.testing import CliRunner
from rich.console import Console

from src.main import app
from src.ui.cli import cli


class TestCLI(unittest.TestCase):
    """Tests para las funcionalidades de CLI."""
    
    def setUp(self):
        """Configuración para los tests."""
        pass
        self.runner = CliRunner()
    
    def test_command_version(self):
        """Verificar que el comando version funciona correctamente."""
        result = self.runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ProjectPrompt", result.stdout)
    
    def test_command_init(self):
        """Verificar que el comando init funciona correctamente."""
        # Test con parámetros
        result = self.runner.invoke(app, ["init", "--name", "test-project"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("test-project", result.stdout)
        self.assertIn("inicializado correctamente", result.stdout)
    
    def test_command_help(self):
        """Verificar que el comando help funciona correctamente."""
        result = self.runner.invoke(app, ["help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Ayuda de ProjectPrompt", result.stdout)
        self.assertIn("Comandos Disponibles", result.stdout)
        
    # No probamos el menú interactivo porque requiere entrada del usuario
    # def test_command_menu(self):
    #    """Verificar que el comando menu funciona correctamente."""
    #    # Este test no se puede automatizar fácilmente porque requiere interacción del usuario
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_methods(self, mock_stdout):
        """Verificar que los métodos de impresión funcionan correctamente."""
        console = Console(file=io.StringIO(), highlight=False)
        
        # Test con un mensaje simple para no depender del formato exacto
        with patch('src.ui.cli.console', console):
            cli.print_success("Test exitoso")
            self.assertIn("Test exitoso", console.file.getvalue())
            
            cli.print_error("Test error")
            self.assertIn("Test error", console.file.getvalue())
            
            cli.print_info("Test info")
            self.assertIn("Test info", console.file.getvalue())


if __name__ == "__main__":
    unittest.main()
