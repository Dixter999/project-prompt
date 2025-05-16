#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plantillas de entrevistas genéricas para cualquier tipo de funcionalidad.

Este módulo contiene preguntas genéricas que se pueden aplicar a cualquier
funcionalidad del proyecto para obtener información relevante.
"""

# Definición de plantillas de entrevistas
INTERVIEW_TEMPLATES = {
    # Plantilla general para cualquier funcionalidad
    'general': {
        # Preguntas iniciales para cualquier funcionalidad
        'initial_questions': [
            {
                'id': 'purpose',
                'question': '¿Cuál es el propósito principal de la funcionalidad {functionality}?',
                'type': 'text'
            },
            {
                'id': 'status',
                'question': '¿Cuál es el estado actual de implementación de {functionality}?',
                'type': 'choice',
                'options': [
                    'No implementado',
                    'Parcialmente implementado',
                    'Implementado pero con problemas',
                    'Completamente implementado'
                ]
            },
            {
                'id': 'requirements',
                'question': '¿Cuáles son los requisitos principales de {functionality}?',
                'type': 'text'
            },
            {
                'id': 'interfaces',
                'question': '¿Con qué otras partes del sistema debe interactuar {functionality}?',
                'type': 'text'
            }
        ],
        
        # Preguntas de seguimiento basadas en respuestas anteriores
        'follow_up_questions': [
            {
                'id': 'challenges',
                'question': '¿Cuáles son los principales desafíos o problemas para implementar {functionality}?',
                'type': 'text',
                'condition': {
                    'type': 'answer_contains',
                    'question_id': 'status',
                    'substring': 'No implementado'
                }
            },
            {
                'id': 'current_problems',
                'question': '¿Qué problemas específicos presenta la implementación actual de {functionality}?',
                'type': 'text',
                'condition': {
                    'type': 'answer_contains',
                    'question_id': 'status',
                    'substring': 'problemas'
                }
            },
            {
                'id': 'completion_needs',
                'question': '¿Qué falta por implementar en {functionality}?',
                'type': 'text',
                'condition': {
                    'type': 'answer_contains',
                    'question_id': 'status',
                    'substring': 'Parcialmente'
                }
            },
            {
                'id': 'tech_stack',
                'question': '¿Qué tecnologías, frameworks o bibliotecas se utilizan o se planean utilizar para {functionality}?',
                'type': 'text'
            },
            {
                'id': 'priority',
                'question': '¿Qué prioridad tiene la implementación o mejora de {functionality}?',
                'type': 'choice',
                'options': ['Baja', 'Media', 'Alta', 'Crítica']
            }
        ],
        
        # Preguntas finales para cualquier funcionalidad
        'final_questions': [
            {
                'id': 'expected_outcome',
                'question': '¿Cuál es el resultado esperado al finalizar la implementación de {functionality}?',
                'type': 'text'
            },
            {
                'id': 'additional_info',
                'question': '¿Hay alguna información adicional relevante sobre {functionality} que no se haya cubierto en las preguntas anteriores?',
                'type': 'text'
            },
            {
                'id': 'suggestions',
                'question': '¿Tienes alguna sugerencia específica para mejorar {functionality}?',
                'type': 'text'
            }
        ]
    },
    
    # Plantilla para funcionalidades relacionadas con la autenticación
    'authentication': {
        'initial_questions': [
            {
                'id': 'auth_type',
                'question': '¿Qué tipo de autenticación se requiere para {functionality}?',
                'type': 'choice',
                'options': [
                    'Local (usuario/contraseña)',
                    'OAuth/OAuth2',
                    'JWT',
                    'SSO (Single Sign-On)',
                    'Autenticación de dos factores',
                    'Otro'
                ]
            },
            {
                'id': 'auth_scope',
                'question': '¿Cuál es el alcance de la autenticación en {functionality}?',
                'type': 'text'
            }
        ],
        'follow_up_questions': [
            {
                'id': 'auth_security',
                'question': '¿Qué requisitos de seguridad existen para la autenticación en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'auth_flow',
                'question': '¿Cómo debería ser el flujo de autenticación para {functionality}?',
                'type': 'text'
            }
        ]
    },
    
    # Plantilla para funcionalidades relacionadas con bases de datos
    'database': {
        'initial_questions': [
            {
                'id': 'db_type',
                'question': '¿Qué tipo de base de datos se utiliza o planea utilizar para {functionality}?',
                'type': 'choice',
                'options': [
                    'Relacional (SQL)',
                    'NoSQL (Documento)',
                    'NoSQL (Clave-valor)',
                    'NoSQL (Columnar)',
                    'NoSQL (Grafo)',
                    'En memoria',
                    'Otro'
                ]
            },
            {
                'id': 'db_schema',
                'question': '¿Cuál es el esquema de datos propuesto para {functionality}?',
                'type': 'text'
            }
        ],
        'follow_up_questions': [
            {
                'id': 'db_performance',
                'question': '¿Hay requisitos específicos de rendimiento para la base de datos en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'db_scalability',
                'question': '¿Cómo debe escalar la solución de base de datos para {functionality}?',
                'type': 'text'
            }
        ]
    },
    
    # Plantilla para funcionalidades relacionadas con la interfaz de usuario
    'user_interface': {
        'initial_questions': [
            {
                'id': 'ui_type',
                'question': '¿Qué tipo de interfaz de usuario se requiere para {functionality}?',
                'type': 'choice',
                'options': [
                    'Web (Frontend)',
                    'Aplicación móvil',
                    'Aplicación de escritorio',
                    'CLI (Interfaz de línea de comandos)',
                    'API',
                    'Otro'
                ]
            },
            {
                'id': 'ui_requirements',
                'question': '¿Cuáles son los requisitos principales de la interfaz de usuario para {functionality}?',
                'type': 'text'
            }
        ],
        'follow_up_questions': [
            {
                'id': 'ui_design',
                'question': '¿Existe un diseño o prototipo para la interfaz de {functionality}?',
                'type': 'boolean'
            },
            {
                'id': 'ui_accessibility',
                'question': '¿Hay requisitos de accesibilidad para la interfaz de {functionality}?',
                'type': 'text'
            }
        ]
    }
}
