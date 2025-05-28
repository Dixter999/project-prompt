#!/usr/bin/env python3
"""
Factory module for ProjectPrompt.

This module provides factory functions to instantiate various components
of the ProjectPrompt system. Using these factory functions helps resolve
circular dependencies by deferring imports until they are needed.
"""

from typing import Optional, Any

# Factory functions for various components

def get_markdown_manager():
    """
    Factory function to create a MarkdownManager instance.
    
    Returns:
        MarkdownManager: A new instance of the MarkdownManager.
    """
    from src.utils.markdown_manager import MarkdownManager
    return MarkdownManager()


def get_markdown_generator():
    """
    Factory function to create a MarkdownGenerator instance.
    
    Returns:
        MarkdownGenerator: A new instance of the MarkdownGenerator.
    """
    from src.generators.markdown_generator import MarkdownGenerator
    return MarkdownGenerator()


def get_project_scanner():
    """
    Factory function to create a ProjectScanner instance.
    
    Returns:
        ProjectScanner: A new instance of the ProjectScanner.
    """
    from src.analyzers.project_scanner import ProjectScanner
    return ProjectScanner()


def get_functionality_detector():
    """
    Factory function to create a FunctionalityDetector instance.
    
    Returns:
        FunctionalityDetector: A new instance of the FunctionalityDetector.
    """
    from src.analyzers.functionality_detector import FunctionalityDetector
    return FunctionalityDetector()


def get_documentation_system():
    """
    Factory function to create a DocumentationSystem instance.
    
    Returns:
        DocumentationSystem: A new instance of the DocumentationSystem.
    """
    from src.utils.documentation_system import DocumentationSystem
    return DocumentationSystem()
