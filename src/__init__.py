"""
ProjectPrompt v2.0 - Simplified AI-powered project analysis.

A refactored version with minimal dependencies and clean architecture.
"""

__version__ = "2.0.0"
__author__ = "ProjectPrompt Team"
__description__ = "AI-powered project analysis and improvement suggestions"

# Core exports
from .core.analyzer import ProjectAnalyzer
from .core.scanner import ProjectScanner
from .core.detector import FunctionalityDetector

from .ai.client import AIClient
from .generators.suggestions import SuggestionGenerator

from .models.project import (
    ProjectAnalysis,
    SuggestionReport,
    ProjectType,
    AnalysisStatus
)

from .utils.config import Config

__all__ = [
    # Core classes
    'ProjectAnalyzer',
    'ProjectScanner', 
    'FunctionalityDetector',
    
    # AI integration
    'AIClient',
    'SuggestionsGenerator',
    
    # Data models
    'ProjectAnalysis',
    'SuggestionReport',
    'ProjectType',
    'AnalysisStatus',
    
    # Configuration
    'get_config',
    'ProjectPromptConfig',
    
    # Version info
    '__version__',
    '__author__',
    '__description__'
]
