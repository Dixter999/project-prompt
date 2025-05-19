#!/usr/bin/env python3
"""
Test de integración para el sistema de generación de prompts.
Verifica la integración entre los analizadores y generadores.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import json
import shutil

# Asegurar que el módulo principal está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.analyzers.project_analyzer import ProjectAnalyzer
from src.generators.prompt_generator import PromptGenerator
from src.generators.contextual_prompt_generator import ContextualPromptGenerator
from src.utils import config


class TestPromptGenerationIntegration(unittest.TestCase):
    """Test de integración para el sistema de generación de prompts."""
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        # Crear un directorio temporal para simular un proyecto
        self.test_dir = tempfile.mkdtemp()
        
        # Crear estructura de archivo de prueba
        self._create_test_project_structure()
        
        # Inicializar el analizador de proyectos
        self.analyzer = ProjectAnalyzer(self.test_dir)
        
        # Cargar configuración simulada
        self.mock_config = {
            "prompt_templates": {
                "default": "Proyecto: {project_name}\nEstructura: {project_structure}\nFuncionalidades: {project_functionality}",
                "code_explanation": "Explica este código: {code_snippet}"
            }
        }
        
        # Mock para config.get_config
        self.config_patcher = patch('src.utils.config.get_config', return_value=self.mock_config)
        self.mock_get_config = self.config_patcher.start()
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        # Eliminar el directorio temporal
        shutil.rmtree(self.test_dir)
        
        # Detener el patcher
        self.config_patcher.stop()
        
    def _create_test_project_structure(self):
        """Crear una estructura de proyecto de prueba en el directorio temporal."""
        # Crear directorios
        os.makedirs(os.path.join(self.test_dir, 'src'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)
        
        # Crear un archivo Python de prueba
        test_content = """
def suma(a, b):
    \"\"\"Suma dos números y devuelve el resultado.\"\"\"
    return a + b

class Calculadora:
    \"\"\"Clase calculadora simple.\"\"\"
    
    def __init__(self):
        \"\"\"Inicializa una nueva calculadora.\"\"\"
        self.historial = []
    
    def sumar(self, a, b):
        \"\"\"Suma dos números y guarda el resultado en el historial.\"\"\"
        resultado = suma(a, b)
        self.historial.append(f"{a} + {b} = {resultado}")
        return resultado
"""
        
        # Escribir archivo
        with open(os.path.join(self.test_dir, 'src', 'calculadora.py'), 'w') as f:
            f.write(test_content)
            
        # Crear un archivo README.md
        readme_content = """
# Proyecto de Calculadora

Este es un proyecto de ejemplo que implementa una calculadora simple.

## Características
- Suma de números
- Historial de operaciones
"""
        
        with open(os.path.join(self.test_dir, 'README.md'), 'w') as f:
            f.write(readme_content)
        
    def test_analyzer_to_generator_integration(self):
        """Verificar que el análisis de proyecto se integra con el generador de prompts."""
        # Ejecutar análisis
        analysis_result = self.analyzer.analyze_project()
        
        # Crear generador de prompts
        generator = PromptGenerator()
        
        # Generar un prompt basado en el análisis
        prompt = generator.generate_prompt("default", {
            "project_name": "Calculadora",
            "project_structure": json.dumps(analysis_result['structure'], indent=2),
            "project_functionality": json.dumps(analysis_result['functionality'], indent=2),
        })
        
        # Verificar que el prompt contiene información del análisis
        self.assertIn("Calculadora", prompt)
        self.assertIn("calculadora.py", prompt)
        
    def test_contextual_prompt_generation(self):
        """Verificar que el generador de prompts contextuales se integra correctamente."""
        # Crear generador contextual
        contextual_generator = ContextualPromptGenerator(self.test_dir)
        
        # Generar un prompt contextual
        file_path = os.path.join(self.test_dir, 'src', 'calculadora.py')
        context = {
            "focus_file": file_path,
            "query": "Explica la clase Calculadora"
        }
        
        # Parche para el análisis del proyecto
        with patch('src.generators.contextual_prompt_generator.ProjectAnalyzer') as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.analyze_project.return_value = {
                'structure': {'directories': [self.test_dir], 'files': [file_path]},
                'functionality': {'classes': ['Calculadora'], 'functions': ['suma']}
            }
            mock_analyzer_class.return_value = mock_analyzer
            
            prompt = contextual_generator.generate_contextual_prompt(context)
            
            # Verificar que el prompt contiene información relevante
            self.assertIn("Calculadora", prompt)
            self.assertIn("clase", prompt.lower())
            
    def test_full_integration_chain(self):
        """Verificar la integración completa desde análisis hasta generación de prompts."""
        # Crear contexto simulado
        context = {
            "focus_file": os.path.join(self.test_dir, 'src', 'calculadora.py'),
            "query": "Explica este código"
        }
        
        # Usar configuración real para este test
        real_config = {
            "prompt_templates": {
                "code_explanation": "Analiza el siguiente código:\n\n{code_snippet}\n\nExplicación detallada:"
            }
        }
        
        with patch('src.utils.config.get_config', return_value=real_config):
            # Crear generador contextual con analizador real
            contextual_generator = ContextualPromptGenerator(self.test_dir)
            
            # Asegurar que lee el archivo real
            prompt = contextual_generator.generate_contextual_prompt(context)
            
            # Verificar que el prompt contiene código del archivo
            self.assertIn("def suma(a, b):", prompt)
            self.assertIn("class Calculadora:", prompt)


if __name__ == '__main__':
    unittest.main()
