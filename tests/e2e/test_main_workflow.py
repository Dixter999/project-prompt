#!/usr/bin/env python3
"""
Test end-to-end para el flujo principal de ProjectPrompt.
Verifica el flujo completo desde análisis hasta generación de prompts y documentación.
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

# Importar el módulo principal
import src.main as main
from typer.testing import CliRunner


class TestMainWorkflow(unittest.TestCase):
    """
    Pruebas end-to-end para el flujo principal de ProjectPrompt.
    Estas pruebas verifican la funcionalidad completa utilizando la API CLI.
    """
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        # Crear un directorio temporal para simular un proyecto
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
        # Crear estructura de proyecto de prueba
        self._create_test_project_structure()
        
        # Crear runner de CLI
        self.runner = CliRunner()
        
        # Configurar patches
        self.ai_patcher = patch('src.integrations.ai_manager.AIManager')
        self.mock_ai_manager = self.ai_patcher.start()
        mock_instance = MagicMock()
        mock_instance.generate_ai_response.return_value = "Respuesta simulada de IA"
        self.mock_ai_manager.return_value = mock_instance
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        # Eliminar el directorio temporal
        shutil.rmtree(self.test_dir)
        
        # Restaurar el directorio de trabajo
        os.chdir(self.original_dir)
        
        # Detener patchers
        self.ai_patcher.stop()
        
    def _create_test_project_structure(self):
        """Crear una estructura de proyecto de prueba en el directorio temporal."""
        # Crear directorios del proyecto
        os.makedirs(os.path.join(self.test_dir, 'src'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'docs'), exist_ok=True)
        
        # Crear archivo Python de prueba
        app_content = """
def main():
    \"\"\"Función principal de la aplicación.\"\"\"
    print("Hola mundo")
    
if __name__ == "__main__":
    main()
"""
        
        # Escribir archivos
        with open(os.path.join(self.test_dir, 'src', 'app.py'), 'w') as f:
            f.write(app_content)
            
        # Crear README
        with open(os.path.join(self.test_dir, 'README.md'), 'w') as f:
            f.write("# Proyecto de Prueba\n\nEste es un proyecto para pruebas e2e.")
    
    @patch('src.main.app')
    def test_analyze_command(self, mock_app):
        """Verificar el comando 'analyze'."""
        # Cambiar al directorio de prueba
        os.chdir(self.test_dir)
        
        # Simular la ejecución del comando
        result = self.runner.invoke(main.app, ["analyze", "--path", self.test_dir])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        
    @patch('src.main.app')
    def test_generate_prompt_command(self, mock_app):
        """Verificar el comando 'generate prompt'."""
        # Cambiar al directorio de prueba
        os.chdir(self.test_dir)
        
        # Simular la ejecución del comando
        result = self.runner.invoke(main.app, ["generate", "prompt", "--path", self.test_dir])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        
    @patch('src.main.app')
    def test_generate_docs_command(self, mock_app):
        """Verificar el comando 'generate docs'."""
        # Cambiar al directorio de prueba
        os.chdir(self.test_dir)
        
        # Simular la ejecución del comando
        result = self.runner.invoke(main.app, ["generate", "docs", "--path", self.test_dir])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        
    @patch('src.main.app')
    def test_full_workflow(self, mock_app):
        """Verificar el flujo de trabajo completo: analizar, generar prompt y documentación."""
        # Cambiar al directorio de prueba
        os.chdir(self.test_dir)
        
        # Análisis
        result_analyze = self.runner.invoke(main.app, ["analyze", "--path", self.test_dir])
        self.assertEqual(result_analyze.exit_code, 0)
        
        # Generar prompt
        result_prompt = self.runner.invoke(main.app, ["generate", "prompt", "--path", self.test_dir])
        self.assertEqual(result_prompt.exit_code, 0)
        
        # Generar documentación
        result_docs = self.runner.invoke(main.app, ["generate", "docs", "--path", self.test_dir])
        self.assertEqual(result_docs.exit_code, 0)
        

if __name__ == '__main__':
    unittest.main()
