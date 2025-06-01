#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Navegador de documentación para ProjectPrompt.

Este módulo proporciona una interfaz para navegar por la documentación
generada por ProjectPrompt, permitiendo listar y ver archivos markdown.
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.tree import Tree
import typer

from src.ui.cli import cli
from src.ui.markdown_viewer import get_markdown_viewer
from src.utils.documentation_system import get_documentation_system
from src.utils.markdown_manager import get_markdown_manager
from src.utils.project_structure import get_project_structure
from src.utils.logger import get_logger

logger = get_logger()

# Create console instance
console = Console()


class DocumentationNavigator:
    """
    Navegador de documentación para ProjectPrompt.
    
    Esta clase proporciona funciones para listar, buscar y visualizar
    la documentación generada por ProjectPrompt.
    """
    
    def __init__(self):
        """Inicializar el navegador de documentación."""
        self.doc_system = get_documentation_system()
        self.markdown_manager = get_markdown_manager()
        self.markdown_viewer = get_markdown_viewer()
        self.project_structure = get_project_structure()
    
    def get_documentation_dir(self, project_path: Optional[str] = None) -> str:
        """
        Obtener el directorio de documentación.
        
        Args:
            project_path: Ruta al proyecto (opcional)
            
        Returns:
            Ruta al directorio de documentación
        """
        # Si no se proporciona ruta, usar el directorio actual
        if not project_path:
            project_path = os.getcwd()
        
        # Verificar si existe un directorio .project-prompt
        docs_dir = os.path.join(project_path, '.project-prompt')
        if os.path.exists(docs_dir):
            return docs_dir
        
        # Si no existe, intentar buscarlo en directorios superiores
        current_dir = project_path
        for _ in range(3):  # Buscar hasta 3 niveles arriba
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Llegamos a la raíz
                break
                
            current_dir = parent_dir
            docs_dir = os.path.join(current_dir, '.project-prompt')
            if os.path.exists(docs_dir):
                return docs_dir
        
        # Si no se encontró, informar al usuario
        cli.print_warning(f"No se encontró documentación en {project_path} o sus directorios padres")
        cli.print_info("Puede generar documentación con: project-prompt analyze")
        return ""
    
    def list_documents(self, docs_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Listar documentos disponibles.
        
        Args:
            docs_dir: Directorio de documentación (opcional)
            
        Returns:
            Lista de documentos encontrados
        """
        if not docs_dir:
            docs_dir = self.get_documentation_dir()
            
        if not docs_dir or not os.path.exists(docs_dir):
            return []
        
        documents = []
        
        # Documentos en la raíz
        root_docs = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) 
                    if f.endswith('.md')]
        
        # Documentos de funcionalidades
        func_dir = os.path.join(docs_dir, 'functionalities')
        func_docs = []
        if os.path.exists(func_dir):
            func_docs = [os.path.join(func_dir, f) for f in os.listdir(func_dir) 
                        if f.endswith('.md')]
        
        # Documentos de prompts
        prompt_dir = os.path.join(docs_dir, 'prompts')
        prompt_docs = []
        if os.path.exists(prompt_dir):
            prompt_docs = [os.path.join(prompt_dir, f) for f in os.listdir(prompt_dir) 
                          if f.endswith('.md')]
            
            # Subdirectorio de funcionalidades
            func_prompt_dir = os.path.join(prompt_dir, 'functionality')
            if os.path.exists(func_prompt_dir):
                func_prompt_docs = [os.path.join(func_prompt_dir, f) 
                                   for f in os.listdir(func_prompt_dir) 
                                   if f.endswith('.md')]
                prompt_docs.extend(func_prompt_docs)
        
        # Procesar todos los documentos
        for doc_path in root_docs + func_docs + prompt_docs:
            try:
                doc_info = self.markdown_manager.get_document_info(doc_path)
                doc_info['path'] = doc_path
                doc_info['relative_path'] = os.path.relpath(doc_path, docs_dir)
                documents.append(doc_info)
            except Exception as e:
                logger.error(f"Error al procesar documento {doc_path}: {e}")
        
        return documents
    
    def show_documents_list(self, docs_dir: Optional[str] = None) -> None:
        """
        Mostrar lista de documentos disponibles.
        
        Args:
            docs_dir: Directorio de documentación (opcional)
        """
        if not docs_dir:
            docs_dir = self.get_documentation_dir()
            
        if not docs_dir or not os.path.exists(docs_dir):
            cli.print_error("No se encontró documentación")
            return
        
        # Obtener documentos
        documents = self.list_documents(docs_dir)
        
        if not documents:
            cli.print_warning("No se encontraron documentos")
            return
        
        # Crear tabla
        table = cli.create_table("Documentos Disponibles", 
                               ["Título", "Tipo", "Actualizado", "Versión", "Ruta"])
        
        # Categorizar documentos
        for doc in documents:
            title = doc.get('title', os.path.basename(doc['path']))
            doc_type = "General"
            
            # Determinar tipo por la ruta
            if 'functionalities' in doc['path']:
                doc_type = "Funcionalidad"
            elif 'prompts/functionality' in doc['path']:
                doc_type = "Prompt de Func."
            elif 'prompts' in doc['path']:
                doc_type = "Prompt"
            
            # Añadir a la tabla
            table.add_row(
                title,
                doc_type,
                doc.get('updated', ""),
                str(doc.get('version', "1")),
                doc['relative_path']
            )
        
        # Mostrar tabla
        console.print(table)
    
    def view_document(self, doc_path: str, show_frontmatter: bool = False) -> None:
        """
        Visualizar un documento específico.
        
        Args:
            doc_path: Ruta al documento o su ruta relativa
            show_frontmatter: Si se debe mostrar el frontmatter
        """
        # Si es una ruta relativa, completar con el directorio de docs
        if not os.path.isabs(doc_path):
            docs_dir = self.get_documentation_dir()
            if not docs_dir:
                return
                
            # Probar diferentes combinaciones
            potential_paths = [
                os.path.join(docs_dir, doc_path),
                os.path.join(docs_dir, 'functionalities', doc_path),
                os.path.join(docs_dir, 'prompts', doc_path),
                os.path.join(docs_dir, 'prompts', 'functionality', doc_path)
            ]
            
            # Si no tiene extensión .md, añadirla
            if not doc_path.endswith('.md'):
                potential_paths.extend([p + '.md' for p in potential_paths])
            
            # Buscar el archivo
            found = False
            for path in potential_paths:
                if os.path.exists(path):
                    doc_path = path
                    found = True
                    break
            
            if not found:
                cli.print_error(f"No se encontró el documento: {doc_path}")
                return
        
        # Visualizar documento
        self.markdown_viewer.view_file(doc_path, show_frontmatter)
    
    def show_documentation_tree(self, docs_dir: Optional[str] = None) -> None:
        """
        Mostrar estructura de documentación como árbol.
        
        Args:
            docs_dir: Directorio de documentación (opcional)
        """
        if not docs_dir:
            docs_dir = self.get_documentation_dir()
            
        if not docs_dir or not os.path.exists(docs_dir):
            cli.print_error("No se encontró documentación")
            return
        
        # Crear árbol
        tree = cli.create_tree("Documentación del Proyecto")
        
        # Función para añadir archivos al árbol
        def add_files_to_tree(directory, parent_node, indent=""):
            try:
                for item in sorted(os.listdir(directory)):
                    item_path = os.path.join(directory, item)
                    
                    if os.path.isdir(item_path):
                        # Es un directorio
                        dir_node = parent_node.add(f"[bold blue]{item}/[/bold blue]")
                        add_files_to_tree(item_path, dir_node, indent + "  ")
                    elif item.endswith('.md'):
                        # Es un archivo markdown
                        try:
                            # Intentar obtener título del documento
                            doc_info = self.markdown_manager.get_document_info(item_path)
                            title = doc_info.get('title', item)
                            parent_node.add(f"[green]{item}[/green] - {title}")
                        except:
                            parent_node.add(f"[green]{item}[/green]")
            except Exception as e:
                logger.error(f"Error al listar directorio {directory}: {e}")
        
        # Añadir archivos al árbol
        add_files_to_tree(docs_dir, tree)
        
        # Mostrar árbol
        console.print(tree)
    
    def show_menu(self) -> None:
        """
        Mostrar menú interactivo de navegación de documentación.
        """
        docs_dir = self.get_documentation_dir()
        if not docs_dir:
            return
            
        documents = self.list_documents(docs_dir)
        if not documents:
            cli.print_warning("No hay documentos disponibles para mostrar")
            return
        
        cli.print_header("Navegador de Documentación")
        
        # Mostrar estructura en árbol
        self.show_documentation_tree(docs_dir)
        
        # Listado de documentos
        console.print("\n[bold cyan]Documentos Disponibles:[/bold cyan]")
        for idx, doc in enumerate(documents, 1):
            title = doc.get('title', os.path.basename(doc['path']))
            rel_path = doc['relative_path']
            console.print(f"[bold]{idx}.[/bold] {title} [dim]({rel_path})[/dim]")
        
        # Selección del usuario
        try:
            choice = Prompt.ask(
                "\nSeleccione un documento para ver (número o q para salir)",
                default="q"
            )
            
            if choice.lower() == 'q':
                return
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(documents):
                    selected_doc = documents[idx]['path']
                    self.view_document(selected_doc)
                else:
                    cli.print_error("Selección fuera de rango")
            except ValueError:
                cli.print_error("Por favor ingrese un número válido")
                
        except KeyboardInterrupt:
            console.print("\nSaliendo del navegador de documentación...")


def get_documentation_navigator() -> DocumentationNavigator:
    """
    Obtener una instancia del navegador de documentación.
    
    Returns:
        Instancia de DocumentationNavigator
    """
    return DocumentationNavigator()
