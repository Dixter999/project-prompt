#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Patrones para detección avanzada de funcionalidades.

Este módulo contiene patrones más específicos para la detección
de funcionalidades comunes en proyectos de software.
"""

from typing import Dict, List, Any

# Importar patrones específicos
from src.templates.functionality_patterns.auth import AUTH_PATTERNS_ADVANCED
from src.templates.functionality_patterns.database import DATABASE_PATTERNS_ADVANCED

# Lista de arquitecturas comunes para reconocimiento
COMMON_ARCHITECTURES = {
    'mvc': {
        'patterns': [
            r'model', r'view', r'controller',
            r'models/', r'views/', r'controllers/',
            r'app/models', r'app/views', r'app/controllers'
        ],
        'description': 'Model-View-Controller',
        'files_required': ['model', 'view', 'controller'],
        'confidence_threshold': 0.7  # 70% de los archivos requeridos deben estar presentes
    },
    'mvvm': {
        'patterns': [
            r'model', r'view', r'viewmodel', 
            r'models/', r'views/', r'viewmodels/',
            r'app/models', r'app/views', r'app/viewmodels'
        ],
        'description': 'Model-View-ViewModel',
        'files_required': ['model', 'view', 'viewmodel'],
        'confidence_threshold': 0.7
    },
    'clean_architecture': {
        'patterns': [
            r'domain', r'usecases', r'repositories', r'entities',
            r'domain/', r'usecases/', r'repositories/', r'entities/',
            r'app/domain', r'app/usecases', r'app/repositories', r'app/entities'
        ],
        'description': 'Clean Architecture',
        'files_required': ['domain', 'usecases', 'entities'],
        'confidence_threshold': 0.7
    },
    'layered': {
        'patterns': [
            r'presentation', r'business', r'data', r'persistence',
            r'presentation/', r'business/', r'data/', r'persistence/',
            r'src/presentation', r'src/business', r'src/data', r'src/persistence'
        ],
        'description': 'Layered Architecture',
        'files_required': ['presentation', 'business', 'data'],
        'confidence_threshold': 0.7
    },
    'hexagonal': {
        'patterns': [
            r'ports', r'adapters', r'application', r'domain',
            r'ports/', r'adapters/', r'application/', r'domain/',
            r'src/ports', r'src/adapters', r'src/application', r'src/domain'
        ],
        'description': 'Hexagonal Architecture / Ports and Adapters',
        'files_required': ['ports', 'adapters', 'domain'],
        'confidence_threshold': 0.7
    },
    'microservices': {
        'patterns': [
            r'service', r'microservice', r'api/gateway', r'discovery', r'registry',
            r'services/', r'microservices/', r'api-gateway', r'service-discovery',
            r'docker-compose.yml', r'kubernetes', r'k8s'
        ],
        'description': 'Microservices Architecture',
        'files_required': ['service', 'docker', 'api'],
        'confidence_threshold': 0.6
    }
}

# Recopilación de todos los patrones avanzados
ADVANCED_FUNCTIONALITY_PATTERNS = {
    'authentication': AUTH_PATTERNS_ADVANCED,
    'database': DATABASE_PATTERNS_ADVANCED
}
