"""
Paquete de analizadores para proyectos.

Este paquete contiene los módulos encargados de analizar la estructura de un proyecto,
detectar sus características principales y generar informes detallados.
"""

from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer
from src.analyzers.functionality_detector import FunctionalityDetector, get_functionality_detector
from src.analyzers.connection_analyzer import ConnectionAnalyzer, get_connection_analyzer
from src.analyzers.dependency_graph import DependencyGraph, get_dependency_graph
from src.analyzers.testability_analyzer import TestabilityAnalyzer, get_testability_analyzer

__all__ = [
    'ProjectScanner', 'get_project_scanner',
    'FileAnalyzer', 'get_file_analyzer',
    'FunctionalityDetector', 'get_functionality_detector',
    'ConnectionAnalyzer', 'get_connection_analyzer',
    'DependencyGraph', 'get_dependency_graph',
    'TestabilityAnalyzer', 'get_testability_analyzer',
]
