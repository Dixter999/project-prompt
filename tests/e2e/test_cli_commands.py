#!/usr/bin/env python3
"""
Test end-to-end para la interfaz de línea de comandos (CLI) de ProjectPrompt.
Verifica la funcionalidad de todos los comandos CLI disponibles.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import shutil
from pathlib import Path

# Asegurar que el módulo principal está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Importar el módulo principal y relacionados con CLI
from src.main import app
from src.ui import cli
from typer.testing import CliRunner


class TestCliCommands(unittest.TestCase):
    """Pruebas end-to-end para todos los comandos CLI de ProjectPrompt."""
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        # Crear runner de CLI
        self.runner = CliRunner()
        
        # Crear un directorio temporal para pruebas
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        # Eliminar el directorio temporal
        shutil.rmtree(self.test_dir)
        
        # Restaurar el directorio de trabajo
        os.chdir(self.original_dir)
        
    def test_help_command(self):
        """Verificar que el comando help funciona correctamente."""
        result = self.runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage:", result.stdout)
        
    @patch('src.main.app')
    def test_version_command(self, mock_app):
        """Verificar que el comando version funciona correctamente."""
        result = self.runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        
    @patch('src.main.app')
    def test_config_commands(self, mock_app):
        """Verificar que los comandos de configuración funcionan correctamente."""
        # Config show
        result_show = self.runner.invoke(app, ["config", "show"])
        self.assertEqual(result_show.exit_code, 0)
        
        # Config set
        result_set = self.runner.invoke(app, ["config", "set", "api_keys.openai", "test-key"])
        self.assertEqual(result_set.exit_code, 0)
        
        # Config reset
        result_reset = self.runner.invoke(app, ["config", "reset"])
        self.assertEqual(result_reset.exit_code, 0)
        
    @patch('src.main.app')
    def test_template_commands(self, mock_app):
        """Verificar que los comandos de plantillas funcionan correctamente."""
        # Template list
        result_list = self.runner.invoke(app, ["template", "list"])
        self.assertEqual(result_list.exit_code, 0)
        
        # Template show
        result_show = self.runner.invoke(app, ["template", "show", "default"])
        self.assertEqual(result_show.exit_code, 0)
        
    @patch('src.main.app')
    def test_update_commands(self, mock_app):
        """Verificar que los comandos de actualización funcionan correctamente."""
        # Update check
        result_check = self.runner.invoke(app, ["update", "check"])
        self.assertEqual(result_check.exit_code, 0)
        
        # Update templates
        result_templates = self.runner.invoke(app, ["update", "templates"])
        self.assertEqual(result_templates.exit_code, 0)
        
    @patch('src.main.app')
    def test_sync_commands(self, mock_app):
        """Verificar que los comandos de sincronización funcionan correctamente."""
        # Sync status
        result_status = self.runner.invoke(app, ["sync", "status"])
        self.assertEqual(result_status.exit_code, 0)
        
        # Sync push
        result_push = self.runner.invoke(app, ["sync", "push"])
        self.assertEqual(result_push.exit_code, 0)
        
        # Sync pull
        result_pull = self.runner.invoke(app, ["sync", "pull"])
        self.assertEqual(result_pull.exit_code, 0)
        
    @patch('src.main.app')
    def test_telemetry_commands(self, mock_app):
        """Verificar que los comandos de telemetría funcionan correctamente."""
        # Telemetry status
        result_status = self.runner.invoke(app, ["telemetry", "status"])
        self.assertEqual(result_status.exit_code, 0)
        
        # Telemetry enable
        result_enable = self.runner.invoke(app, ["telemetry", "enable"])
        self.assertEqual(result_enable.exit_code, 0)
        
        # Telemetry disable
        result_disable = self.runner.invoke(app, ["telemetry", "disable"])
        self.assertEqual(result_disable.exit_code, 0)
        
        # Telemetry prompt
        result_prompt = self.runner.invoke(app, ["telemetry", "prompt"])
        self.assertEqual(result_prompt.exit_code, 0)
        
    @patch('src.main.app')
    def test_interactive_mode(self, mock_app):
        """Verificar que el modo interactivo se inicia correctamente."""
        # Comando interactive
        result = self.runner.invoke(app, ["interactive"])
        self.assertEqual(result.exit_code, 0)
        

if __name__ == '__main__':
    unittest.main()
