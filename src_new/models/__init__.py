"""
Models module for ProjectPrompt.
Contains all data models and structures.
"""

from .project import (
    ProjectAnalysis,
    SuggestionReport,
    Suggestion,
    ProjectType,
    AnalysisStatus,
    ProjectStructure,
    FileInfo,
    DirectoryInfo,
    FunctionalityDetection,
    AIResponse,
    ProjectReport,
    ScanConfig,
    AnalysisConfig,
    ExportConfig
)

__all__ = [
    'ProjectAnalysis',
    'SuggestionReport', 
    'Suggestion',
    'ProjectType',
    'AnalysisStatus',
    'ProjectStructure',
    'FileInfo',
    'DirectoryInfo',
    'FunctionalityDetection',
    'AIResponse',
    'ProjectReport',
    'ScanConfig',
    'AnalysisConfig',
    'ExportConfig'
]