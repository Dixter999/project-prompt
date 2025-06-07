"""
Paquete de analizadores para proyectos.

Este paquete contiene los módulos encargados de analizar la estructura de un proyecto,
detectar sus características principales y generar informes detallados.
"""

# Core analyzers maintained in Fase 1
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.analyzers.dependency_graph import DependencyGraph, get_dependency_graph
from src.analyzers.functionality_detector import FunctionalityDetector, get_functionality_detector
from src.analyzers.ai_group_analyzer import AIGroupAnalyzer

# Supporting analyzers (to evaluate in Phase 2)
from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer
from src.analyzers.completeness_verifier import CompletenessVerifier, get_completeness_verifier
from src.analyzers.project_structure_analyzer import ProjectStructureAnalyzer, get_project_structure_analyzer
from src.analyzers.rules_suggester import RulesSuggester, get_rules_suggester
from src.models.suggestion_models import SuggestionContext

__all__ = [
    # Core analyzers (Fase 1 maintained)
    'ProjectScanner', 'get_project_scanner',
    'DependencyGraph', 'get_dependency_graph', 
    'FunctionalityDetector', 'get_functionality_detector',
    'AIGroupAnalyzer',
    
    # Supporting analyzers (to review in Phase 2)
    'FileAnalyzer', 'get_file_analyzer',
    'CompletenessVerifier', 'get_completeness_verifier',
    'ProjectStructureAnalyzer', 'get_project_structure_analyzer',
    'RulesSuggester', 'get_rules_suggester', 
    'SuggestionContext',
]
