#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para el detector de funcionalidades.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path
import shutil

# Add the project root to path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.functionality_detector import FunctionalityDetector, get_functionality_detector
from src.templates.common_functionalities import FUNCTIONALITY_PATTERNS, DETECTION_WEIGHTS

class TestFunctionalityDetector(unittest.TestCase):
    """Tests para el detector de funcionalidades de proyectos."""
    
    def setUp(self):
        """Configuración para los tests."""
        self.detector = get_functionality_detector()
        
        # Crear directorio temporal para archivos de prueba
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpieza después de los tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_detector_initialization(self):
        """Probar la correcta inicialización del detector."""
        self.assertIsInstance(self.detector, FunctionalityDetector)
        self.assertEqual(self.detector.functionalities, {})
        self.assertEqual(self.detector.evidence, {})
        self.assertEqual(self.detector.confidence_scores, {})

    def test_get_functionality_detector(self):
        """Probar la función de fábrica para obtener el detector."""
        detector = get_functionality_detector()
        self.assertIsInstance(detector, FunctionalityDetector)
    
    def _create_test_project_with_auth(self):
        """Crea un proyecto de prueba con características de autenticación."""
        # Crear estructura de directorios
        auth_dir = os.path.join(self.temp_dir, "auth")
        os.makedirs(auth_dir)
        
        # Crear archivo de autenticación
        auth_file = os.path.join(auth_dir, "login.py")
        with open(auth_file, "w") as f:
            f.write("import jwt\nimport bcrypt\n\n")
            f.write("def authenticate(username, password):\n")
            f.write("    # Verify password hash\n")
            f.write("    return bcrypt.checkpw(password.encode(), stored_hash)\n\n")
            f.write("def generate_token(user_id):\n")
            f.write("    return jwt.encode({'user_id': user_id}, 'secret_key')\n")
        
        # Crear archivo de configuración
        config_file = os.path.join(self.temp_dir, "config.py")
        with open(config_file, "w") as f:
            f.write("SECRET_KEY = 'super_secret_key_for_jwt'\n")
            f.write("AUTH_ENABLED = True\n")
            f.write("SESSION_TIMEOUT = 3600\n")
        
        return self.temp_dir
    
    def _create_test_project_with_db(self):
        """Crea un proyecto de prueba con características de base de datos."""
        # Crear estructura de directorios
        models_dir = os.path.join(self.temp_dir, "models")
        os.makedirs(models_dir)
        
        # Crear archivo de modelo
        model_file = os.path.join(models_dir, "user.py")
        with open(model_file, "w") as f:
            f.write("from sqlalchemy import Column, String, Integer\n")
            f.write("from sqlalchemy.ext.declarative import declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write("class User(Base):\n")
            f.write("    __tablename__ = 'users'\n")
            f.write("    id = Column(Integer, primary_key=True)\n")
            f.write("    username = Column(String, unique=True)\n")
        
        # Crear archivo de configuración de BD
        db_config = os.path.join(self.temp_dir, "database.py")
        with open(db_config, "w") as f:
            f.write("from sqlalchemy import create_engine\n\n")
            f.write("DATABASE_URL = 'postgresql://user:pass@localhost/dbname'\n")
            f.write("engine = create_engine(DATABASE_URL)\n")
        
        return self.temp_dir
    
    def _create_test_project_with_api(self):
        """Crea un proyecto de prueba con características de API."""
        # Crear estructura de directorios
        api_dir = os.path.join(self.temp_dir, "api")
        os.makedirs(api_dir)
        
        # Crear archivo de controlador API
        controller_file = os.path.join(api_dir, "user_controller.py")
        with open(controller_file, "w") as f:
            f.write("from fastapi import APIRouter, Depends\n\n")
            f.write("router = APIRouter(prefix='/api/users')\n\n")
            f.write("@router.get('/')\n")
            f.write("def get_users():\n")
            f.write("    return {'users': []}\n\n")
            f.write("@router.post('/')\n")
            f.write("def create_user(user_data: dict):\n")
            f.write("    return {'id': 1, **user_data}\n")
        
        return self.temp_dir
    
    def _create_test_project_with_frontend(self):
        """Crea un proyecto de prueba con características de frontend."""
        # Crear estructura de directorios
        components_dir = os.path.join(self.temp_dir, "components")
        os.makedirs(components_dir)
        
        # Crear archivo de componente React
        component_file = os.path.join(components_dir, "UserList.jsx")
        with open(component_file, "w") as f:
            f.write("import React, { useState, useEffect } from 'react';\n\n")
            f.write("const UserList = () => {\n")
            f.write("  const [users, setUsers] = useState([]);\n\n")
            f.write("  useEffect(() => {\n")
            f.write("    fetch('/api/users').then(res => res.json()).then(data => setUsers(data.users));\n")
            f.write("  }, []);\n\n")
            f.write("  return (\n")
            f.write("    <div className='user-list'>\n")
            f.write("      {users.map(user => <div key={user.id}>{user.name}</div>)}\n")
            f.write("    </div>\n")
            f.write("  );\n")
            f.write("};\n\n")
            f.write("export default UserList;\n")
        
        return self.temp_dir
    
    def _create_test_project_with_tests(self):
        """Crea un proyecto de prueba con características de tests."""
        # Crear estructura de directorios
        tests_dir = os.path.join(self.temp_dir, "tests")
        os.makedirs(tests_dir)
        
        # Crear archivo de test unitario
        test_file = os.path.join(tests_dir, "test_user.py")
        with open(test_file, "w") as f:
            f.write("import unittest\n")
            f.write("import pytest\n\n")
            f.write("from models.user import User\n\n")
            f.write("class TestUser(unittest.TestCase):\n")
            f.write("    def test_user_creation(self):\n")
            f.write("        user = User(username='test')\n")
            f.write("        self.assertEqual(user.username, 'test')\n\n")
            f.write("    def test_user_validation(self):\n")
            f.write("        user = User(username='')\n")
            f.write("        self.assertFalse(user.is_valid())\n\n")
            f.write("@pytest.fixture\n")
            f.write("def sample_user():\n")
            f.write("    return User(username='testuser')\n")
        
        return self.temp_dir
    
    def _create_complete_test_project(self):
        """Crea un proyecto de prueba con todas las funcionalidades."""
        self._create_test_project_with_auth()
        self._create_test_project_with_db()
        self._create_test_project_with_api()
        self._create_test_project_with_frontend()
        self._create_test_project_with_tests()
        return self.temp_dir
    
    def test_detect_auth_functionality(self):
        """Probar la detección de funcionalidad de autenticación."""
        project_path = self._create_test_project_with_auth()
        result = self.detector.detect_functionalities(project_path)
        
        self.assertTrue(result['detected']['authentication']['present'])
        self.assertGreaterEqual(result['detected']['authentication']['confidence'], 50)
        self.assertIn('authentication', result['main_functionalities'])
    
    def test_detect_db_functionality(self):
        """Probar la detección de funcionalidad de base de datos."""
        project_path = self._create_test_project_with_db()
        result = self.detector.detect_functionalities(project_path)
        
        self.assertTrue(result['detected']['database']['present'])
        self.assertGreaterEqual(result['detected']['database']['confidence'], 50)
        self.assertIn('database', result['main_functionalities'])
    
    def test_detect_api_functionality(self):
        """Probar la detección de funcionalidad de API."""
        project_path = self._create_test_project_with_api()
        result = self.detector.detect_functionalities(project_path)
        
        self.assertTrue(result['detected']['api']['present'])
        self.assertGreaterEqual(result['detected']['api']['confidence'], 50)
        self.assertIn('api', result['main_functionalities'])
    
    def test_detect_frontend_functionality(self):
        """Probar la detección de funcionalidad de frontend."""
        project_path = self._create_test_project_with_frontend()
        result = self.detector.detect_functionalities(project_path)
        
        self.assertTrue(result['detected']['frontend']['present'])
        self.assertGreaterEqual(result['detected']['frontend']['confidence'], 50)
        self.assertIn('frontend', result['main_functionalities'])
    
    def test_detect_test_functionality(self):
        """Probar la detección de funcionalidad de tests."""
        project_path = self._create_test_project_with_tests()
        result = self.detector.detect_functionalities(project_path)
        
        self.assertTrue(result['detected']['tests']['present'])
        self.assertGreaterEqual(result['detected']['tests']['confidence'], 50)
        self.assertIn('tests', result['main_functionalities'])
    
    def test_detect_complete_project(self):
        """Probar la detección en un proyecto con todas las funcionalidades."""
        project_path = self._create_complete_test_project()
        result = self.detector.detect_functionalities(project_path)
        
        # Verificar que todas las funcionalidades están presentes
        for functionality in ['authentication', 'database', 'api', 'frontend', 'tests']:
            self.assertTrue(result['detected'][functionality]['present'])
            self.assertIn(functionality, result['main_functionalities'])
    
    def test_get_functionality_info(self):
        """Probar la obtención de información detallada de una funcionalidad."""
        project_path = self._create_test_project_with_auth()
        self.detector.detect_functionalities(project_path)
        
        info = self.detector.get_functionality_info('authentication')
        self.assertEqual(info['name'], 'authentication')
        self.assertTrue(info['present'])
        self.assertGreaterEqual(info['confidence'], 50)
        self.assertIn('files', info['evidence'])
        self.assertIn('imports', info['evidence'])
    
    def test_summarize_functionalities(self):
        """Probar la generación de un resumen de funcionalidades."""
        project_path = self._create_complete_test_project()
        self.detector.detect_functionalities(project_path)
        
        summary = self.detector.summarize_functionalities()
        self.assertIsInstance(summary, str)
        self.assertIn("Funcionalidades detectadas", summary)
        for functionality in ['Authentication', 'Database', 'Api', 'Frontend', 'Tests']:
            self.assertIn(functionality, summary)


if __name__ == '__main__':
    unittest.main()
