#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Factory module for ProjectPrompt.

This module provides factory functions to create instances of various
classes in the system. It helps avoid circular imports by centralizing
the creation logic.
"""

# These imports are lazy-loaded inside the functions to avoid circular imports
# Only add TYPE_CHECKING imports here
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from src.utils.config import ConfigManager
    from src.utils.markdown_manager import MarkdownManager
    from src.generators.markdown_generator import MarkdownGenerator
    from src.analyzers.project_scanner import ProjectScanner
    from src.analyzers.functionality_detector import FunctionalityDetector
    from src.utils.documentation_system import DocumentationSystem


def get_config_manager() -> 'ConfigManager':
    """Get a ConfigManager instance."""
    from src.utils.config import ConfigManager
    return ConfigManager()


def get_markdown_manager(templates_dir: Optional[str] = None) -> 'MarkdownManager':
    """Get a MarkdownManager instance."""
    from src.utils.markdown_manager import MarkdownManager
    return MarkdownManager(templates_dir)


def get_markdown_generator(template_dir: Optional[str] = None) -> 'MarkdownGenerator':
    """Get a MarkdownGenerator instance."""
    from src.generators.markdown_generator import MarkdownGenerator
    return MarkdownGenerator(template_dir)


def get_project_scanner() -> 'ProjectScanner':
    """Get a ProjectScanner instance."""
    from src.analyzers.project_scanner import ProjectScanner
    return ProjectScanner()


def get_functionality_detector() -> 'FunctionalityDetector':
    """Get a FunctionalityDetector instance."""
    from src.analyzers.functionality_detector import FunctionalityDetector
    return FunctionalityDetector()


def get_documentation_system() -> 'DocumentationSystem':
    """Get a DocumentationSystem instance."""
    from src.utils.documentation_system import DocumentationSystem
    return DocumentationSystem()
