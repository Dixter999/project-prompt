"""
Paquete de analizadores para proyectos.

Este paquete contiene los módulos encargados de analizar la estructura de un proyecto,
detectar sus características principales y generar informes detallados.
"""

from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer

__all__ = [
    'ProjectScanner', 'get_project_scanner',
    'FileAnalyzer', 'get_file_analyzer',
]
