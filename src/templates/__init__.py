"""
Módulo para plantillas y templates.

Este paquete contiene plantillas y definiciones de patrones
comunes usados en diferentes tipos de proyectos.
"""

from src.templates.common_functionalities import (
    FUNCTIONALITY_PATTERNS,
    AUTH_PATTERNS,
    DATABASE_PATTERNS,
    API_PATTERNS,
    FRONTEND_PATTERNS,
    TEST_PATTERNS,
    DETECTION_WEIGHTS,
    CONFIDENCE_THRESHOLD
)

__all__ = [
    'FUNCTIONALITY_PATTERNS',
    'AUTH_PATTERNS',
    'DATABASE_PATTERNS',
    'API_PATTERNS',
    'FRONTEND_PATTERNS',
    'TEST_PATTERNS',
    'DETECTION_WEIGHTS',
    'CONFIDENCE_THRESHOLD'
]
