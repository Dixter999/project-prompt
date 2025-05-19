#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plantillas de entrevistas específicas para integración de APIs.

Este módulo contiene preguntas especializadas para funcionalidades
relacionadas con integración de APIs externas o internas.
"""

# Definición de plantillas para entrevistas sobre APIs
INTERVIEW_TEMPLATES = {
    # Plantilla general para APIs
    'general': {
        # Preguntas iniciales para APIs
        'initial_questions': [
            {
                'id': 'api_purpose',
                'question': '¿Cuál es el propósito principal de la integración con API para {functionality}?',
                'type': 'text'
            },
            {
                'id': 'api_type',
                'question': '¿Qué tipo de API se utiliza o se planea utilizar en {functionality}?',
                'type': 'choice',
                'options': [
                    'REST',
                    'GraphQL',
                    'SOAP',
                    'gRPC',
                    'WebSockets',
                    'Webhook',
                    'Otro'
                ]
            },
            {
                'id': 'api_provider',
                'question': '¿Es una API interna o externa? Si es externa, ¿quién es el proveedor?',
                'type': 'text'
            },
            {
                'id': 'api_endpoints',
                'question': '¿Qué endpoints o operaciones principales se utilizan en {functionality}?',
                'type': 'text'
            }
        ],
        
        # Preguntas de seguimiento para APIs
        'follow_up_questions': [
            {
                'id': 'api_auth',
                'question': '¿Qué método de autenticación utiliza la API en {functionality}?',
                'type': 'choice',
                'options': [
                    'API Key',
                    'OAuth/OAuth2',
                    'JWT',
                    'Autenticación básica',
                    'Sin autenticación',
                    'Otro'
                ]
            },
            {
                'id': 'api_rate_limits',
                'question': '¿Hay límites de tasa (rate limits) en la API que afecten a {functionality}?',
                'type': 'boolean'
            },
            {
                'id': 'api_rate_limit_details',
                'question': '¿Cuáles son los detalles de los límites de tasa de la API?',
                'type': 'text',
                'condition': {
                    'type': 'answer_boolean',
                    'question_id': 'api_rate_limits',
                    'is_true': True
                }
            },
            {
                'id': 'api_data_format',
                'question': '¿Qué formato de datos utiliza la API en {functionality}?',
                'type': 'choice',
                'options': ['JSON', 'XML', 'Protobuf', 'YAML', 'Texto plano', 'Binario', 'Otro']
            },
            {
                'id': 'api_error_handling',
                'question': '¿Cómo se manejan los errores de la API en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'api_async',
                'question': '¿La integración con la API es síncrona o asíncrona?',
                'type': 'choice',
                'options': ['Síncrona', 'Asíncrona', 'Ambas', 'No definido']
            }
        ],
        
        # Preguntas finales para APIs
        'final_questions': [
            {
                'id': 'api_tests',
                'question': '¿Cómo se realizan o planean realizar las pruebas de integración con la API en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'api_fallback',
                'question': '¿Existe algún plan de contingencia o fallback si la API no está disponible en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'api_monitoring',
                'question': '¿Cómo se monitorea el rendimiento y disponibilidad de la API en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'api_future',
                'question': '¿Hay planes futuros de cambios o evolución en la integración con la API en {functionality}?',
                'type': 'text'
            }
        ]
    },
    
    # Plantilla específica para APIs REST
    'rest_api': {
        'initial_questions': [
            {
                'id': 'rest_http_methods',
                'question': '¿Qué métodos HTTP se utilizan en la API REST para {functionality}?',
                'type': 'choice',
                'options': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'Varios de los anteriores']
            },
            {
                'id': 'rest_resource_structure',
                'question': '¿Cuál es la estructura de recursos principal de la API REST en {functionality}?',
                'type': 'text'
            }
        ],
        'follow_up_questions': [
            {
                'id': 'rest_versioning',
                'question': '¿Cómo se maneja el versionado de la API REST en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'rest_pagination',
                'question': '¿Se utiliza paginación en la API REST? Si es así, ¿cómo funciona?',
                'type': 'text'
            }
        ]
    },
    
    # Plantilla específica para APIs GraphQL
    'graphql_api': {
        'initial_questions': [
            {
                'id': 'graphql_schema',
                'question': '¿Cuál es el esquema GraphQL principal utilizado en {functionality}?',
                'type': 'text'
            },
            {
                'id': 'graphql_operations',
                'question': '¿Qué tipos de operaciones GraphQL (queries, mutations, subscriptions) se utilizan en {functionality}?',
                'type': 'text'
            }
        ],
        'follow_up_questions': [
            {
                'id': 'graphql_batching',
                'question': '¿Se utiliza batching o alguna estrategia de optimización de consultas en GraphQL para {functionality}?',
                'type': 'text'
            },
            {
                'id': 'graphql_fragments',
                'question': '¿Se utilizan fragmentos GraphQL en {functionality}? ¿Con qué finalidad?',
                'type': 'text'
            }
        ]
    }
}
