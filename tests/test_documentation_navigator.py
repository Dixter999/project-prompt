#!/usr/bin/env python3
"""
Tests para el navegador de documentación.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from rich.console import Console

from src.main import app
from src.ui.documentation_navigator import DocumentationNavigator, get_documentation_navigator
from src.utils.markdown_manager import get_markdown_manager
from src.utils.documentation_system import get_documentation_system


class TestDocumentationNavigator(unittest.TestCase):
    """Tests para el navegador de documentación."""
    
    def setUp(self):
        """Configurar el entorno de prueba."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.docs_dir = self.test_dir / ".project-prompt"
        self.docs_dir.mkdir()
        
        # Crear estructura de documentación para pruebas
        self.func_dir = self.docs_dir / "functionalities"
        self.func_dir.mkdir()
        
        self.prompts_dir = self.docs_dir / "prompts"
        self.prompts_dir.mkdir()
        
        self.func_prompts_dir = self.prompts_dir / "functionality"
        self.func_prompts_dir.mkdir()
        
        # Crear algunos documentos de prueba
        self.project_doc = self.docs_dir / "project-analysis.md"
        with open(self.project_doc, "w") as f:
            f.write("---\ntitle: Análisis del Proyecto\nversion: 1\n---\n\n# Análisis del Proyecto\n\nEste es un documento de prueba.")
            
        self.func_doc = self.func_dir / "auth.md"
        with open(self.func_doc, "w") as f:
            f.write("---\ntitle: Funcionalidad: Autenticación\nversion: 2\n---\n\n# Autenticación\n\nFuncionalidad de autenticación.")
            
        # Inicializar navegador
        with patch('src.ui.markdown_viewer.get_markdown_viewer'):
            with patch('src.utils.markdown_manager.get_markdown_manager'):
                with patch('src.utils.documentation_system.get_documentation_system'):
                    self.navigator = DocumentationNavigator()
        
        # Runner para pruebas de CLI
        self.runner = CliRunner()
    
    def tearDown(self):
        """Limpiar después de las pruebas."""
        self.temp_dir.cleanup()
    
    def test_get_documentation_dir(self):
        """Probar la detección del directorio de documentación."""
        # Caso: directorio existente
        with patch('src.ui.cli.cli.print_warning'):
            with patch('src.ui.cli.cli.print_info'):
                result = self.navigator.get_documentation_dir(str(self.test_dir))
                self.assertEqual(result, str(self.docs_dir))
        
        # Caso: directorio no existente
        with patch('src.ui.cli.cli.print_warning'):
            with patch('src.ui.cli.cli.print_info'):
                result = self.navigator.get_documentation_dir(str(self.test_dir / "nonexistent"))
                self.assertEqual(result, "")
    
    @patch('src.utils.markdown_manager.get_markdown_manager')
    def test_list_documents(self, mock_get_manager):
        """Probar el listado de documentos."""
        # Mock para el markdown manager
        mock_manager = MagicMock()
        mock_manager.get_document_info.side_effect = lambda path: {
            'title': 'Análisis del Proyecto' if 'project-analysis' in path else 'Funcionalidad: Autenticación',
            'version': 1 if 'project-analysis' in path else 2,
        }
        mock_get_manager.return_value = mock_manager
        
        # Mock para get_documentation_dir
        with patch.object(self.navigator, 'get_documentation_dir', return_value=str(self.docs_dir)):
            self.navigator.markdown_manager = mock_manager
            docs = self.navigator.list_documents()
            self.assertEqual(len(docs), 2)  # project-analysis.md y auth.md
    
    @patch('src.ui.documentation_navigator.console.print')
    def test_show_documents_list(self, mock_print):
        """Probar la visualización de la lista de documentos."""
        with patch.object(self.navigator, 'get_documentation_dir', return_value=str(self.docs_dir)):
            with patch.object(self.navigator, 'list_documents', return_value=[
                {'title': 'Análisis del Proyecto', 'path': str(self.project_doc), 
                 'relative_path': 'project-analysis.md', 'version': 1},
                {'title': 'Funcionalidad: Autenticación', 'path': str(self.func_doc), 
                 'relative_path': 'functionalities/auth.md', 'version': 2}
            ]):
                self.navigator.show_documents_list()
                mock_print.assert_called()
    
    @patch('src.ui.markdown_viewer.MarkdownViewer.view_file')
    def test_view_document(self, mock_view):
        """Probar la visualización de un documento."""
        # Vista de documento existente
        with patch.object(self.navigator, 'get_documentation_dir', return_value=str(self.docs_dir)):
            # Mock para el markdown_viewer
            mock_viewer = MagicMock()
            self.navigator.markdown_viewer = mock_viewer
            
            # Prueba con ruta directa
            self.navigator.view_document(str(self.project_doc))
            mock_viewer.view_file.assert_called_with(str(self.project_doc), False)
    
    @patch('src.ui.documentation_navigator.console.print')
    def test_show_documentation_tree(self, mock_print):
        """Probar la visualización de la estructura en árbol."""
        with patch.object(self.navigator, 'get_documentation_dir', return_value=str(self.docs_dir)):
            with patch('src.ui.cli.cli.create_tree'):
                self.navigator.show_documentation_tree()
                mock_print.assert_called()
    
    def test_docs_command_help(self):
        """Probar el comando de ayuda de documentación en CLI."""
        # Verificar que el comando existe y muestra la ayuda
        with patch('src.ui.documentation_navigator.get_documentation_navigator'):
            result = self.runner.invoke(app, ["docs", "--help"])
            self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
