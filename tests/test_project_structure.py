#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el gestor de estructura del proyecto.
"""

import os
import tempfile
import shutil
import unittest
from pathlib import Path
import yaml

from src.utils.project_structure import ProjectStructure, get_project_structure

class TestProjectStructure(unittest.TestCase):
    """Pruebas para la clase ProjectStructure."""

    def setUp(self):
        """Configuración previa a cada prueba."""
        # Crear directorio temporal para las pruebas
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuración de prueba
        self.test_config = {
            'project_name': 'Test Project',
            'version': '0.1.0',
            'language': 'es'
        }
        
        # Crear instancia de ProjectStructure
        self.structure = ProjectStructure(self.temp_dir, self.test_config)

    def tearDown(self):
        """Limpieza después de cada prueba."""
        # Eliminar directorio temporal
        shutil.rmtree(self.temp_dir)

    def test_create_structure(self):
        """Probar la creación de la estructura básica de archivos."""
        # Crear la estructura
        result = self.structure.create_structure()
        
        # Verificar que la estructura fue creada
        self.assertEqual(result['status'], 'created')
        
        # Verificar directorios creados
        root_dir = os.path.join(self.temp_dir, '.project-prompt')
        self.assertTrue(os.path.exists(root_dir))
        
        # Verificar directorios específicos
        functionalities_dir = os.path.join(root_dir, 'functionalities')
        prompts_dir = os.path.join(root_dir, 'prompts')
        prompts_func_dir = os.path.join(root_dir, 'prompts/functionality')
        
        self.assertTrue(os.path.exists(functionalities_dir))
        self.assertTrue(os.path.exists(prompts_dir))
        self.assertTrue(os.path.exists(prompts_func_dir))
        
        # Verificar archivos básicos
        analysis_file = os.path.join(root_dir, 'project-analysis.md')
        config_file = os.path.join(root_dir, 'config.yaml')
        prompt_file = os.path.join(prompts_dir, 'general.md')
        
        self.assertTrue(os.path.exists(analysis_file))
        self.assertTrue(os.path.exists(config_file))
        self.assertTrue(os.path.exists(prompt_file))
        
        # Verificar contenido del archivo de configuración
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        self.assertEqual(config_data['project_name'], 'Test Project')
        self.assertEqual(config_data['version'], '0.1.0')
        self.assertEqual(config_data['language'], 'es')

    def test_get_structure_info(self):
        """Probar la obtención de información de la estructura."""
        # Crear la estructura
        self.structure.create_structure()
        
        # Obtener información
        info = self.structure.get_structure_info()
        
        # Verificar información básica
        self.assertTrue(info['exists'])
        self.assertEqual(info['structure_root'], os.path.join(self.temp_dir, '.project-prompt'))
        self.assertTrue(info['has_analysis'])
        self.assertTrue(info['has_config'])
        
    def test_save_functionality_files(self):
        """Probar la creación de archivos para una funcionalidad."""
        # Crear la estructura base
        self.structure.create_structure()
        
        # Crear archivos para una funcionalidad
        func_name = "auth"
        analysis_content = "# Análisis de autenticación\n\nEste es un análisis de prueba."
        prompt_content = "# Prompt para autenticación\n\nEste es un prompt de prueba."
        
        # Guardar archivos
        analysis_path = self.structure.save_functionality_analysis(func_name, analysis_content)
        prompt_path = self.structure.save_functionality_prompt(func_name, prompt_content)
        
        # Verificar que los archivos existen
        self.assertTrue(os.path.exists(analysis_path))
        self.assertTrue(os.path.exists(prompt_path))
        
        # Verificar contenido
        with open(analysis_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Análisis de autenticación", content)
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Prompt para autenticación", content)
        
        # Obtener información actualizada
        info = self.structure.get_structure_info()
        
        # Verificar que la funcionalidad aparece en la información
        self.assertIn("auth", info['functionalities'])
        self.assertIn("auth", info['prompts'])
    
    def test_clear_structure(self):
        """Probar la eliminación de toda la estructura."""
        # Crear la estructura
        self.structure.create_structure()
        
        # Verificar que la estructura existe
        root_dir = os.path.join(self.temp_dir, '.project-prompt')
        self.assertTrue(os.path.exists(root_dir))
        
        # Eliminar la estructura
        result = self.structure.clear_structure(confirm=True)
        self.assertTrue(result)
        
        # Verificar que la estructura ya no existe
        self.assertFalse(os.path.exists(root_dir))
    
    def test_get_project_structure_function(self):
        """Probar la función auxiliar get_project_structure."""
        # Obtener una instancia usando la función auxiliar
        structure = get_project_structure(self.temp_dir, self.test_config)
        
        # Verificar que es una instancia de ProjectStructure
        self.assertIsInstance(structure, ProjectStructure)
        
        # Verificar que tiene la configuración correcta
        self.assertEqual(structure.config['project_name'], 'Test Project')


if __name__ == '__main__':
    unittest.main()
