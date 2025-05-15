#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para los analizadores de proyecto.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path
import shutil

from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner


class TestFileAnalyzer(unittest.TestCase):
    """Tests para el analizador de archivos."""
    
    def setUp(self):
        """Configuración para los tests."""
        self.analyzer = get_file_analyzer()
        
        # Crear directorio temporal para archivos de prueba
        self.temp_dir = tempfile.mkdtemp()
        
        # Crear un archivo de texto
        self.text_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test file\nWith multiple lines\n")
            
        # Crear un archivo Python
        self.py_file = os.path.join(self.temp_dir, "example.py")
        with open(self.py_file, "w") as f:
            f.write("#!/usr/bin/env python\n")
            f.write("import os\nimport sys\nfrom pathlib import Path\n\n")
            f.write("def main():\n    print('Hello world!')\n\n")
            f.write("if __name__ == '__main__':\n    main()\n")
            
    def tearDown(self):
        """Limpieza después de los tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_file_type(self):
        """Probar la detección del tipo de archivo."""
        # Analizar archivo de texto
        info = self.analyzer.get_file_type(self.text_file)
        self.assertEqual(info["extension"], ".txt")
        self.assertFalse(info["is_binary"])
        
        # Analizar archivo Python
        info = self.analyzer.get_file_type(self.py_file)
        self.assertEqual(info["extension"], ".py")
        self.assertEqual(info["language"], "Python")
        self.assertFalse(info["is_binary"])
    
    def test_extract_dependencies(self):
        """Probar la extracción de dependencias."""
        # Extraer dependencias de archivo Python
        deps = self.analyzer.extract_dependencies(self.py_file, "Python")
        self.assertIn("os", deps)
        self.assertIn("sys", deps)
        self.assertIn("pathlib", deps)


class TestProjectScanner(unittest.TestCase):
    """Tests para el escáner de proyectos."""
    
    def setUp(self):
        """Configuración para los tests."""
        self.scanner = get_project_scanner()
        
        # Crear estructura de directorios de prueba
        self.temp_dir = tempfile.mkdtemp()
        
        # Crear directorios
        os.makedirs(os.path.join(self.temp_dir, "src", "utils"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        
        # Crear archivos
        with open(os.path.join(self.temp_dir, "README.md"), "w") as f:
            f.write("# Test Project\nThis is a test project.\n")
            
        with open(os.path.join(self.temp_dir, "src", "main.py"), "w") as f:
            f.write("import sys\nfrom utils import helper\n\nprint('Main module')\n")
            
        with open(os.path.join(self.temp_dir, "src", "utils", "helper.py"), "w") as f:
            f.write("def help_func():\n    return 'Helper function'\n")
            
        with open(os.path.join(self.temp_dir, "tests", "test_main.py"), "w") as f:
            f.write("import unittest\nfrom src import main\n\n")
            f.write("class TestMain(unittest.TestCase):\n    pass\n")
            
    def tearDown(self):
        """Limpieza después de los tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_scan_project(self):
        """Probar el escaneo completo de un proyecto."""
        result = self.scanner.scan_project(self.temp_dir)
        
        # Verificar estructura básica
        self.assertEqual(result["project_path"], self.temp_dir)
        self.assertIn("structure", result)
        self.assertIn("files", result)
        self.assertIn("stats", result)
        
        # Verificar estadísticas
        stats = result["stats"]
        self.assertEqual(stats["total_files"], 4)  # README + 3 archivos Python
        self.assertEqual(stats["total_dirs"], 4)   # root + src + utils + tests
        
        # Verificar lenguajes
        self.assertIn("Python", result["languages"])
        self.assertIn("Markdown", result["languages"])
        
        # Verificar archivos importantes
        self.assertIn("main", result["important_files"])
        self.assertIn("documentation", result["important_files"])


if __name__ == "__main__":
    unittest.main()
