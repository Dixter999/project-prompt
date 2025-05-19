#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plantillas de prompts para generación de texto con IA.

Este módulo contiene las plantillas de prompts contextuales
que se utilizarán para generar sugerencias sobre proyectos.
"""

from typing import Dict, List, Any

# Plantilla para descripción general del proyecto
PROJECT_DESCRIPTION_TEMPLATE = """
# Análisis del proyecto: {project_name}

## Descripción básica para asistente IA

### Estructura general
El proyecto analizado contiene {file_count} archivos distribuidos en {dir_count} directorios.
Los lenguajes principales detectados son: {main_languages}.

### Archivos importantes
Los archivos principales detectados son:
{important_files}

### Estructura de dependencias
Las dependencias principales del proyecto son:
{main_dependencies}

### Contexto técnico
Este proyecto parece ser {project_type_description} y utiliza {framework_description}.

Por favor, genera una descripción general de este proyecto, explicando su propósito aparente 
y arquitectura basándote en esta información.
"""

# Plantilla para sugerencias de mejora
IMPROVEMENT_SUGGESTIONS_TEMPLATE = """
# Sugerencias de mejora para: {project_name}

## Contexto para generar sugerencias

### Estructura del proyecto
- Archivos totales: {file_count}
- Directorios: {dir_count}
- Lenguajes principales: {main_languages}

### Características detectadas
{detected_features}

### Posibles áreas de mejora
1. Estructura de archivos: {file_structure_complexity}
2. Patrones de código: {code_patterns}
3. Dependencias: {dependency_count} dependencias detectadas

Basado en esta información, genera 3-5 sugerencias concretas para mejorar la organización,
calidad de código o arquitectura del proyecto. Enfócate especialmente en buenas prácticas
para proyectos de {main_language}.
"""

# Plantilla para identificación de problemas potenciales
POTENTIAL_ISSUES_TEMPLATE = """
# Análisis de problemas potenciales: {project_name}

## Contexto para identificación de problemas

### Datos generales
- Tamaño total: {total_size} KB
- Archivos: {file_count} ({binary_count} binarios)
- Lenguajes: {main_languages}

### Indicadores de complejidad
- Archivos por directorio: {files_per_dir}
- Promedio de tamaño de archivo: {avg_file_size} KB
- Archivos grandes (>100KB): {large_files_count}

### Patrones detectados
{detected_patterns}

Basado en esta información, identifica 2-3 posibles problemas técnicos que podrían afectar
la mantenibilidad, escalabilidad o rendimiento del proyecto. Proporciona una explicación
breve de cada problema y su potencial impacto.
"""

# Plantillas adicionales para versión freemium
FREE_TEMPLATES = {
    'description': PROJECT_DESCRIPTION_TEMPLATE,
    'improvements': IMPROVEMENT_SUGGESTIONS_TEMPLATE,
    'issues': POTENTIAL_ISSUES_TEMPLATE
}

# Mapping de funcionalidades a tipos de aplicaciones
PROJECT_TYPE_HINTS = {
    'api': ["API", "servicio web", "backend"],
    'database': ["aplicación con base de datos", "sistema de almacenamiento de datos"],
    'authentication': ["aplicación con sistema de autenticación", "sistema con login"],
    'frontend': ["aplicación web frontend", "interfaz de usuario"],
    'tests': ["proyecto con pruebas automatizadas"]
}

# Frases comunes para describir el propósito de diferentes tipos de funcionalidades
FUNCTIONALITY_DESCRIPTIONS = {
    'api': "expone endpoints para interacción con otros sistemas",
    'database': "almacena y gestiona datos persistentes",
    'authentication': "implementa controles de acceso y seguridad",
    'frontend': "presenta una interfaz visual para usuarios",
    'tests': "incluye validación automatizada de funcionalidades"
}

# Frameworks comunes asociados con diferentes lenguajes
COMMON_FRAMEWORKS = {
    'python': ["Django", "Flask", "FastAPI", "Pytest", "SQLAlchemy"],
    'javascript': ["React", "Angular", "Vue", "Express", "Jest"],
    'typescript': ["Angular", "React con TypeScript", "NestJS", "TypeORM"],
    'java': ["Spring", "Hibernate", "JUnit", "Jakarta EE"],
    'csharp': ["ASP.NET", "Entity Framework", "xUnit", "Blazor"],
    'php': ["Laravel", "Symfony", "PHPUnit", "Doctrine"],
    'ruby': ["Ruby on Rails", "Sinatra", "RSpec", "ActiveRecord"]
}

# Frases pre-generadas para cada tipo de prompt
PREGENERATED_PHRASES = {
    'description': [
        "Este proyecto parece ser una aplicación web completa con frontend y backend.",
        "El código sugiere una API REST con múltiples endpoints.",
        "La estructura indica que se trata de una biblioteca o paquete reutilizable.",
        "El proyecto implementa una aplicación de línea de comandos con varias funcionalidades.",
        "Este parece ser un proyecto de análisis de datos o aprendizaje automático."
    ],
    'improvements': [
        "Considerar añadir más pruebas unitarias para mejorar la cobertura.",
        "La estructura de directorios podría reorganizarse para seguir un patrón estándar.",
        "Implementar un sistema de documentación automatizada.",
        "Revisar y actualizar las dependencias obsoletas.",
        "Añadir tipos estáticos para mejorar la seguridad del código."
    ],
    'issues': [
        "Posible acoplamiento excesivo entre módulos.",
        "Falta de manejo de errores en operaciones críticas.",
        "Redundancia de código que podría abstraerse en funciones comunes.",
        "Vulnerabilidades potenciales en la gestión de autenticación.",
        "Problemas de escalabilidad en la forma de gestionar las conexiones a la base de datos."
    ]
}
