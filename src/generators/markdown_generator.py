#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la generación de reportes en formato Markdown.

Este módulo proporciona funcionalidades para generar reportes
detallados sobre la estructura y composición de un proyecto.
"""

import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, TYPE_CHECKING
import jinja2

from src import __version__
from src.utils.logger import get_logger

# Using TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.analyzers.project_scanner import ProjectScanner

# Configurar logger
logger = get_logger()

class MarkdownGenerator:
    """Generador de reportes en formato Markdown."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Inicializar el generador de markdown.
        
        Args:
            template_dir: Directorio opcional donde se encuentran las plantillas
        """
        if template_dir is None:
            # Usar el directorio predeterminado de plantillas
            module_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(module_dir, "templates")
        
        self.template_dir = template_dir
        
        # Configurar entorno Jinja
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            keep_trailing_newline=True
        )
        
        # Registrar filtros personalizados
        self.jinja_env.filters['file_to_id'] = self._file_to_id
        self.jinja_env.filters['filename'] = self._get_filename
    
    def _file_to_id(self, file_path: str) -> str:
        """
        Convertir una ruta de archivo a un ID válido para gráficos (Mermaid).
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            ID válido para gráficos
        """
        # Eliminar caracteres especiales y espacios, y usar guiones bajos
        return re.sub(r'[^a-zA-Z0-9]', '_', file_path)
    
    def _get_filename(self, file_path: str) -> str:
        """
        Obtener solo el nombre del archivo de una ruta.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Nombre del archivo
        """
        return os.path.basename(file_path)
        
    def generate_directory_tree(self, structure: Dict[str, Any], 
                                max_depth: int = 5, 
                                ignore_patterns: Optional[List[str]] = None,
                                current_depth: int = 0) -> str:
        """
        Generar una representación en texto del árbol de directorios.
        
        Args:
            structure: Estructura de directorios
            max_depth: Profundidad máxima a mostrar
            ignore_patterns: Patrones a ignorar
            current_depth: Profundidad actual (para recursión)
            
        Returns:
            Texto representando el árbol de directorios
        """
        if ignore_patterns is None:
            ignore_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env']
            
        if current_depth >= max_depth:
            return "..."
            
        result = []
        
        # Si es la raíz, comenzar con el punto
        if current_depth == 0:
            result.append(".")
            
        # Obtener contenidos (directorios y archivos)
        contents = structure.get('contents', {})
        
        # Filtrar según patrones a ignorar
        filtered_contents = {
            name: item for name, item in contents.items() 
            if not any(pattern in name for pattern in ignore_patterns)
        }
        
        # Procesar directorios y archivos
        items = sorted(filtered_contents.items(), 
                     key=lambda x: (x[1].get('type') != 'directory', x[0]))
        
        for i, (name, item) in enumerate(items):
            # Determinar prefijo según posición
            prefix = "└── " if i == len(items) - 1 else "├── "
            
            # Agregar línea actual
            indent = "    " * current_depth
            result.append(f"{indent}{prefix}{name}")
            
            # Si es directorio, procesar recursivamente
            if item.get('type') == 'directory' and current_depth < max_depth - 1:
                # Determinar prefijo para líneas de hijos
                child_prefix = "    " if i == len(items) - 1 else "│   "
                
                # Llamar recursivamente y ajustar indentación
                subtree = self.generate_directory_tree(
                    item, max_depth, ignore_patterns, current_depth + 1
                )
                
                if subtree and subtree != "...":
                    subtree_lines = subtree.split("\n")
                    for line in subtree_lines:
                        if line:  # Evitar líneas vacías
                            result.append(f"{indent}{child_prefix}{line}")
        
        return "\n".join(result)
    
    def generate_project_report(self, project_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Generar un reporte completo del proyecto en formato Markdown.
        
        Args:
            project_data: Datos del análisis del proyecto
            output_path: Ruta opcional para guardar el reporte
            
        Returns:
            Contenido del reporte generado
        """
        try:
            # Cargar plantilla
            template = self.jinja_env.get_template("project_report.md")
            
            # Preparar datos para la plantilla
            project_name = os.path.basename(project_data.get('project_path', ''))
            if not project_name:
                project_name = "Proyecto Sin Nombre"
                
            # Generar árbol de directorios
            directory_tree = self.generate_directory_tree(project_data.get('structure', {}))
            
            template_data = {
                'project_name': project_name,
                'project_path': project_data.get('project_path', ''),
                'version': __version__,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                'stats': project_data.get('stats', {}),
                'languages': project_data.get('languages', {}),
                'important_files': project_data.get('important_files', {}),
                'dependencies': project_data.get('dependencies', {}),
                'dependency_graph': project_data.get('dependency_graph', {}),
                'directory_tree': directory_tree
            }
            
            # Renderizar plantilla
            report_content = template.render(**template_data)
            
            # Guardar archivo si se especificó una ruta
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"Reporte guardado en: {output_path}")
                
            return report_content
            
        except Exception as e:
            logger.error(f"Error al generar reporte Markdown: {e}")
            raise
    
    def save_project_report(self, project_path: str, output_dir: Optional[str] = None) -> str:
        """
        Analizar un proyecto y guardar un reporte completo.
        
        Args:
            project_path: Ruta del proyecto a analizar
            output_dir: Directorio opcional donde guardar el reporte
            
        Returns:
            Ruta al archivo generado
        """
        try:
            # Importar aquí para evitar importaciones circulares
            from src.analyzers.project_scanner import get_project_scanner
            
            # Crear scanner de proyectos
            scanner = get_project_scanner()
            
            # Realizar análisis
            project_data = scanner.scan_project(project_path)
            
            # Generar grafo de dependencias
            project_data['dependency_graph'] = scanner.get_dependency_graph(max_items=15)
            
            # Determinar directorio de salida
            if not output_dir:
                # Usar directorio .project-prompt dentro del proyecto
                output_dir = os.path.join(project_path, '.project-prompt')
                
            os.makedirs(output_dir, exist_ok=True)
                
            # Nombre del archivo
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
            project_name = os.path.basename(project_path)
            filename = f"{project_name}_analysis_{timestamp}.md"
            output_path = os.path.join(output_dir, filename)
            
            # Generar reporte
            self.generate_project_report(project_data, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al guardar reporte del proyecto: {e}")
            raise


def get_markdown_generator(template_dir: Optional[str] = None) -> MarkdownGenerator:
    """
    Obtener una instancia del generador de Markdown.
    
    Args:
        template_dir: Directorio opcional donde se encuentran las plantillas
        
    Returns:
        Instancia de MarkdownGenerator
    """
    return MarkdownGenerator(template_dir=template_dir)
