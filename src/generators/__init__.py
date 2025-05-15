"""
Paquete de generadores para ProjectPrompt.

Este paquete contiene los módulos encargados de generar
diferentes tipos de reportes y documentación.
"""

from src.generators.markdown_generator import MarkdownGenerator, get_markdown_generator

__all__ = [
    'MarkdownGenerator', 'get_markdown_generator',
]
