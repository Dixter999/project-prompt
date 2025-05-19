#!/usr/bin/env python3
"""
Test de integración para el subsistema de análisis de proyectos.
Verifica que los diferentes analizadores trabajen correctamente juntos.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import shutil
from pathlib import Path

# Asegurar que el módulo principal está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.analyzers import project_structure_analyzer
from src.analyzers import functionality_detector
from src.analyzers import connection_analyzer
from src.analyzers.project_analyzer import ProjectAnalyzer


class TestProjectAnalysisIntegration(unittest.TestCase):
    """Test de integración para el sistema completo de análisis de proyectos."""
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        # Crear un directorio temporal para simular un proyecto
        self.test_dir = tempfile.mkdtemp()
        
        # Crear estructura de archivo de prueba
        self._create_test_project_structure()
        
        # Inicializar el analizador de proyectos
        self.analyzer = ProjectAnalyzer(self.test_dir)
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        # Eliminar el directorio temporal
        shutil.rmtree(self.test_dir)
        
    def _create_test_project_structure(self):
        """Crear una estructura de proyecto de prueba en el directorio temporal."""
        # Crear directorios
        os.makedirs(os.path.join(self.test_dir, 'src', 'models'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'src', 'controllers'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'src', 'views'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)
        
        # Crear archivos Python de prueba
        model_content = """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
    def validate(self):
        return '@' in self.email
"""
        
        controller_content = """
from src.models.user import User

class UserController:
    def __init__(self, database):
        self.database = database
        
    def create_user(self, name, email):
        user = User(name, email)
        if user.validate():
            self.database.save(user)
            return user
        return None
"""
        
        view_content = """
from src.controllers.user_controller import UserController

class UserView:
    def __init__(self, controller):
        self.controller = controller
        
    def render_create_form(self):
        return "<form>Create User</form>"
        
    def handle_create_submission(self, form_data):
        name = form_data.get('name')
        email = form_data.get('email')
        return self.controller.create_user(name, email)
"""
        
        # Escribir archivos
        with open(os.path.join(self.test_dir, 'src', 'models', 'user.py'), 'w') as f:
            f.write(model_content)
            
        with open(os.path.join(self.test_dir, 'src', 'controllers', 'user_controller.py'), 'w') as f:
            f.write(controller_content)
            
        with open(os.path.join(self.test_dir, 'src', 'views', 'user_view.py'), 'w') as f:
            f.write(view_content)
            
        # Crear un archivo __init__.py en cada directorio
        for dir_path in [
            os.path.join(self.test_dir, 'src'),
            os.path.join(self.test_dir, 'src', 'models'),
            os.path.join(self.test_dir, 'src', 'controllers'),
            os.path.join(self.test_dir, 'src', 'views'),
        ]:
            with open(os.path.join(dir_path, '__init__.py'), 'w') as f:
                f.write('# Init file')
        
    def test_full_project_analysis(self):
        """Verificar que el análisis completo del proyecto funciona correctamente."""
        # Ejecutar análisis
        analysis_result = self.analyzer.analyze_project()
        
        # Verificar que el resultado contiene datos de cada analizador
        self.assertTrue('structure' in analysis_result)
        self.assertTrue('functionality' in analysis_result)
        self.assertTrue('connections' in analysis_result)
        
        # Verificar que se detectó la estructura de directorios
        structure = analysis_result['structure']
        self.assertTrue(any('src' in item for item in structure['directories']))
        self.assertTrue(any('models' in item for item in structure['directories']))
        
        # Verificar que se detectaron funcionalidades
        functionality = analysis_result['functionality']
        self.assertTrue(any('User' in str(item) for item in functionality['classes']))
        
        # Verificar que se detectaron conexiones
        connections = analysis_result['connections']
        self.assertTrue(any('user.py' in str(conn) and 'user_controller.py' in str(conn) 
                            for conn in connections['imports']))
        
    def test_structure_analyzer_integration(self):
        """Verificar que el analizador de estructura trabaja correctamente."""
        structure = project_structure_analyzer.analyze_project_structure(self.test_dir)
        
        self.assertTrue('directories' in structure)
        self.assertTrue('files' in structure)
        self.assertTrue('file_types' in structure)
        
        # Verificar directorios
        self.assertTrue(any('src' in dir_path for dir_path in structure['directories']))
        
        # Verificar archivos
        self.assertTrue(any('user.py' in file_path for file_path in structure['files']))
        
        # Verificar tipos de archivos
        self.assertTrue('py' in structure['file_types'])
        
    def test_functionality_detector_integration(self):
        """Verificar que el detector de funcionalidades trabaja correctamente."""
        functionality = functionality_detector.detect_functionality(self.test_dir)
        
        self.assertTrue('classes' in functionality)
        self.assertTrue('functions' in functionality)
        
        # Verificar clases detectadas
        self.assertTrue(any('User' in cls for cls in functionality['classes']))
        
    def test_connection_analyzer_integration(self):
        """Verificar que el analizador de conexiones trabaja correctamente."""
        connections = connection_analyzer.analyze_connections(self.test_dir)
        
        self.assertTrue('imports' in connections)
        self.assertTrue('dependencies' in connections)
        
        # Verificar importaciones
        user_controller_imports = [imp for imp in connections['imports'] 
                                  if 'user_controller.py' in str(imp)]
        self.assertTrue(len(user_controller_imports) > 0)
        
    @patch('src.analyzers.project_analyzer.ProjectAnalyzer._generate_report')
    def test_report_generation(self, mock_generate_report):
        """Verificar que la generación de reportes se integra correctamente."""
        self.analyzer.generate_analysis_report()
        mock_generate_report.assert_called_once()


if __name__ == '__main__':
    unittest.main()
