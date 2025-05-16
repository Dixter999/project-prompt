#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visor de archivos markdown para ProjectPrompt.

Este módulo proporciona funciones para mostrar contenido markdown
en la terminal con formato enriquecido.
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich import print as rich_print
from rich.syntax import Syntax
import frontmatter
from pygments.lexers import get_lexer_by_name

from src.utils.logger import get_logger

logger = get_logger()
console = Console()


class MarkdownViewer:
    """
    Visor de archivos markdown con formato enriquecido para la terminal.
    
    Esta clase permite visualizar documentos markdown con resaltado de
    sintaxis y elementos como encabezados, listas, enlaces, etc.
    """
    
    def __init__(self):
        """Inicializar el visor de markdown."""
        self.console = Console()
    
    def view_file(self, file_path: str, show_frontmatter: bool = False,
                 show_metadata: bool = True) -> None:
        """
        Mostrar el contenido de un archivo markdown.
        
        Args:
            file_path: Ruta al archivo markdown
            show_frontmatter: Si se debe mostrar el frontmatter en crudo
            show_metadata: Si se debe mostrar el metadata como panel informativo
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"El archivo no existe: {file_path}")
                self.console.print(f"[bold red]Error:[/bold red] El archivo {file_path} no existe")
                return
            
            # Leer el archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
            # Mostrar información del documento si se solicita
            if show_metadata:
                self._display_metadata(post, file_path)
            
            # Mostrar frontmatter en crudo si se solicita
            if show_frontmatter:
                self._display_frontmatter(post)
            
            # Renderizar contenido Markdown
            md = Markdown(post.content)
            self.console.print(md)
        
        except Exception as e:
            logger.error(f"Error al mostrar archivo markdown: {e}", exc_info=True)
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    def _display_metadata(self, post: frontmatter.Post, file_path: str) -> None:
        """
        Mostrar metadatos del documento en un panel informativo.
        
        Args:
            post: Objeto frontmatter.Post
            file_path: Ruta al archivo
        """
        meta = post.metadata
        
        # Contenido del panel
        panel_content = []
        
        # Título
        if 'title' in meta:
            panel_content.append(f"[bold cyan]{meta['title']}[/bold cyan]")
        else:
            panel_content.append(f"[bold cyan]{os.path.basename(file_path)}[/bold cyan]")
        
        # Información de versión
        if 'version' in meta:
            panel_content.append(f"Versión: [yellow]{meta['version']}[/yellow]")
        
        # Fechas de creación y actualización
        if 'created' in meta:
            panel_content.append(f"Creado: {meta.get('created', 'Desconocido')}")
        if 'updated' in meta:
            panel_content.append(f"Actualizado: {meta.get('updated', 'Desconocido')}")
        
        # Si hay algún elemento especial, mostrarlo
        special_keys = ['functionality', 'project_name', 'generated_by']
        for key in special_keys:
            if key in meta:
                panel_content.append(f"{key.replace('_', ' ').title()}: {meta[key]}")
        
        # Crear y mostrar panel
        panel_text = "\n".join(panel_content)
        panel = Panel(panel_text, title="Información del Documento", border_style="blue")
        self.console.print(panel)
        self.console.print()  # Línea en blanco para separar
    
    def _display_frontmatter(self, post: frontmatter.Post) -> None:
        """
        Mostrar el frontmatter en crudo con resaltado de sintaxis.
        
        Args:
            post: Objeto frontmatter.Post
        """
        import yaml
        
        # Convertir metadata a YAML
        yaml_text = yaml.dump(post.metadata, default_flow_style=False)
        
        # Mostrar con resaltado
        self.console.print("Frontmatter:")
        syntax = Syntax(yaml_text, "yaml", theme="monokai", line_numbers=True)
        self.console.print(syntax)
        self.console.print()  # Línea en blanco para separar


def get_markdown_viewer() -> MarkdownViewer:
    """
    Obtener una instancia del visor de markdown.
    
    Returns:
        Instancia de MarkdownViewer
    """
    return MarkdownViewer()
