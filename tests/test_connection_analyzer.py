#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para el análisis de conexiones entre archivos.
"""

import os
import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch

from src.analyzers.connection_analyzer import get_connection_analyzer
from src.analyzers.dependency_graph import get_dependency_graph


class TestConnectionAnalysis(unittest.TestCase):
    """Test case for file connection analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.connection_analyzer = get_connection_analyzer()
        self.dependency_graph = get_dependency_graph()
        
        # Create simple test project
        self._create_test_project()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_basic_connection_analysis(self):
        """Test basic connection analysis functionality."""
        # Analyze connections
        connections = self.connection_analyzer.analyze_connections(self.test_dir)
        
        # Basic assertions
        self.assertIsNotNone(connections)
        self.assertEqual(connections['project_path'], self.test_dir)
        self.assertGreater(connections['files_analyzed'], 0)
        
        # Check if some connections were detected
        self.assertIn('file_connections', connections)
        
        # Check if some example files in connections
        file_imports = connections['file_imports']
        self.assertGreater(len(file_imports), 0)
        
        # Verificar que se registran exclusiones
        self.assertIn('files_excluded', connections)
        excluded = connections['files_excluded']
        self.assertIsInstance(excluded, dict)
        self.assertIn('total_excluded', excluded)
    
    def test_dependency_graph_generation(self):
        """Test dependency graph generation."""
        # Generate graph
        graph = self.dependency_graph.build_dependency_graph(self.test_dir)
        
        # Basic assertions
        self.assertIsNotNone(graph)
        self.assertIn('nodes', graph)
        self.assertIn('edges', graph)
        self.assertIn('metrics', graph)
        
        # Check metrics are calculated
        metrics = graph['metrics']
        self.assertIn('nodes', metrics)
        self.assertIn('edges', metrics)
        self.assertIn('density', metrics)
    
    def test_markdown_visualization(self):
        """Test markdown visualization generation."""
        # Generate graph
        graph = self.dependency_graph.build_dependency_graph(self.test_dir)
        
        # Generate markdown
        markdown = self.dependency_graph.generate_markdown_visualization(graph)
        
        # Basic assertions
        self.assertIsNotNone(markdown)
        self.assertGreater(len(markdown), 100)  # Should be reasonably sized
        self.assertIn("# Grafo de Dependencias", markdown)
    
    def test_file_exclusion(self):
        """Test that non-relevant files are properly excluded."""
        # Crear algunos archivos que deberían ser excluidos
        multimedia_dir = self.test_dir / "assets"
        multimedia_dir.mkdir()
        
        # Archivos multimedia
        (multimedia_dir / "image.jpg").write_text("dummy image content")
        (multimedia_dir / "video.mp4").write_text("dummy video content")
        
        # HTML puramente presentacional
        html_file = multimedia_dir / "presentational.html"
        html_file.write_text("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Presentational HTML</title>
            <meta charset="utf-8">
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <h1>This is a static HTML</h1>
            <p>With no functional code</p>
        </body>
        </html>
        """)
        
        # HTML funcional
        functional_html = multimedia_dir / "functional.html"
        functional_html.write_text("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Functional HTML</title>
            <script src="app.js"></script>
        </head>
        <body>
            <h1>This has JavaScript</h1>
            <button onclick="doSomething()">Click me</button>
            <script>
                function doSomething() {
                    console.log("Hello world");
                }
            </script>
        </body>
        </html>
        """)
        
        # Realizar análisis
        connections = self.connection_analyzer.analyze_connections(self.test_dir)
        
        # Verificar que se excluyeron archivos
        self.assertIn('files_excluded', connections)
        excluded = connections['files_excluded']
        self.assertGreater(excluded['by_extension'], 0)  # Debería excluir jpg y mp4
        
        # Verificar que el HTML funcional no se excluyó pero el presentacional sí
        functional_path = os.path.relpath(functional_html, self.test_dir)
        presentational_path = os.path.relpath(html_file, self.test_dir)
        
        # El HTML funcional debería estar en file_imports
        file_imports = connections['file_imports']
        html_files_found = [f for f in file_imports.keys() if f.endswith('.html')]
        
        # Al menos un HTML funcional debe estar incluido
        self.assertGreaterEqual(len(html_files_found), 1)
        # El HTML presentacional no debe estar incluido
        for html_file in html_files_found:
            self.assertNotEqual(html_file, presentational_path)
    
    def _create_test_project(self):
        """Create a simple test project structure for analysis."""
        # Create main directory
        src_dir = self.test_dir / "src"
        src_dir.mkdir()
        
        # Create main module
        main_py = src_dir / "main.py"
        main_py.write_text("""
import os
import sys
from src.utils import helper
from src.models.user import User

def main():
    user = User("test")
    helper.process(user)

if __name__ == "__main__":
    main()
""")
        
        # Create utils directory
        utils_dir = src_dir / "utils"
        utils_dir.mkdir()
        
        # Create helper module
        helper_py = utils_dir / "helper.py"
        helper_py.write_text("""
import json
from src.models.user import User
from src.config import settings

def process(user):
    print(f"Processing {user.name}")
    config = settings.get_config()
    return json.dumps({"user": user.name, "config": config})
""")
        
        # Create init file
        init_py = utils_dir / "__init__.py"
        init_py.write_text("# Utils package")
        
        # Create models directory
        models_dir = src_dir / "models"
        models_dir.mkdir()
        
        # Create user module
        user_py = models_dir / "user.py"
        user_py.write_text("""
class User:
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
""")
        
        # Create init file
        init_py = models_dir / "__init__.py"
        init_py.write_text("# Models package")
        
        # Create config directory
        config_dir = src_dir / "config"
        config_dir.mkdir()
        
        # Create settings module
        settings_py = config_dir / "settings.py"
        settings_py.write_text("""
import os
from src.utils.helper import process

def get_config():
    return {
        "env": os.environ.get("ENV", "development")
    }

# This creates a circular dependency with helper.py
""")
        
        # Create init file
        init_py = config_dir / "__init__.py"
        init_py.write_text("# Config package")


if __name__ == '__main__':
    unittest.main()
