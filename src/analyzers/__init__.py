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
from src.analyzers.completeness_verifier import CompletenessVerifier, get_completeness_verifier
from src.analyzers.code_quality_analyzer import CodeQualityAnalyzer, get_code_quality_analyzer
from src.analyzers.project_progress_tracker import ProjectProgressTracker, get_project_progress_tracker

__all__ = [
    'ProjectScanner', 'get_project_scanner',
    'FileAnalyzer', 'get_file_analyzer',
    'FunctionalityDetector', 'get_functionality_detector',
    'ConnectionAnalyzer', 'get_connection_analyzer',
    'ProjectProgressTracker', 'get_project_progress_tracker',
    'DependencyGraph', 'get_dependency_graph',
    'TestabilityAnalyzer', 'get_testability_analyzer',
    'CompletenessVerifier', 'get_completeness_verifier',
    'CodeQualityAnalyzer', 'get_code_quality_analyzer',
]
