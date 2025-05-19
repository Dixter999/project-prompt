#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para el generador de reportes en Markdown.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import json

from src.analyzers.project_scanner import get_project_scanner
from src.generators.markdown_generator import MarkdownGenerator, get_markdown_generator


class TestMarkdownGenerator(unittest.TestCase):
    """Tests para el generador de reportes Markdown."""
    
    def setUp(self):
        """Configuración para los tests."""
        self.generator = get_markdown_generator()
        
        # Crear directorio temporal para archivos de prueba
        self.temp_dir = tempfile.mkdtemp()
        
        # Crear una estructura de directorios y archivos para prueba
        os.makedirs(os.path.join(self.temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        
        with open(os.path.join(self.temp_dir, "README.md"), "w") as f:
            f.write("# Test Project\nThis is a test project.\n")
            
        with open(os.path.join(self.temp_dir, "src", "main.py"), "w") as f:
            f.write("print('Hello world!')\n")
            
        with open(os.path.join(self.temp_dir, "tests", "test_main.py"), "w") as f:
            f.write("def test_main():\n    pass\n")
            
        # Escanear el proyecto de prueba
        scanner = get_project_scanner()
        self.project_data = scanner.scan_project(self.temp_dir)
            
    def tearDown(self):
        """Limpieza después de los tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_directory_tree(self):
        """Probar la generación del árbol de directorios."""
        tree = self.generator.generate_directory_tree(self.project_data['structure'])
        
        # Verificar que el árbol contenga elementos esperados
        self.assertIn(".", tree)
        self.assertIn("README.md", tree)
        self.assertIn("src", tree)
        self.assertIn("tests", tree)
    
    def test_generate_project_report(self):
        """Probar la generación del reporte completo."""
        # Generar reporte
        report = self.generator.generate_project_report(self.project_data)
        
        # Verificar secciones principales
        self.assertIn("# Análisis de Proyecto", report)
        self.assertIn("## 📊 Resumen del Proyecto", report)
        self.assertIn("## 📁 Estructura del Proyecto", report)
        
        # Verificar contenido específico
        self.assertIn(os.path.basename(self.temp_dir), report)  # Debe contener el nombre del proyecto
        self.assertIn("README.md", report)  # Debe mencionar el archivo README
        
    def test_save_project_report(self):
        """Probar el guardado del reporte a un archivo."""
        # Definir directorio de salida
        output_dir = os.path.join(self.temp_dir, ".project-prompt")
        
        # Generar y guardar reporte
        report_path = self.generator.save_project_report(self.temp_dir, output_dir)
        
        # Verificar que el archivo existe
        self.assertTrue(os.path.isfile(report_path))
        
        # Verificar que el contenido es correcto
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# Análisis de Proyecto", content)
            self.assertIn(os.path.basename(self.temp_dir), content)


if __name__ == "__main__":
    unittest.main()
