"""
Simplified core module for ProjectPrompt.

Contains the main analysis components:
- ProjectScanner: file and structure scanning
- FunctionalityDetector: functionality detection
- ProjectAnalyzer: unified analysis
"""

from .scanner import ProjectScanner
from .detector import FunctionalityDetector
from .analyzer import ProjectAnalyzer

__all__ = [
    'ProjectScanner',
    'FunctionalityDetector', 
    'ProjectAnalyzer'
]