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

from src.templates.prompt_templates import (
    FREE_TEMPLATES,
    PROJECT_TYPE_HINTS,
    FUNCTIONALITY_DESCRIPTIONS,
    COMMON_FRAMEWORKS,
    PREGENERATED_PHRASES
)

__all__ = [
    'FUNCTIONALITY_PATTERNS',
    'AUTH_PATTERNS',
    'DATABASE_PATTERNS',
    'API_PATTERNS',
    'FRONTEND_PATTERNS',
    'TEST_PATTERNS',
    'DETECTION_WEIGHTS',
    'CONFIDENCE_THRESHOLD',
    'FREE_TEMPLATES',
    'PROJECT_TYPE_HINTS',
    'FUNCTIONALITY_DESCRIPTIONS',
    'COMMON_FRAMEWORKS',
    'PREGENERATED_PHRASES'
]
