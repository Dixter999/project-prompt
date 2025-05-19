#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plantilla especializada para propuestas de implementación de autenticación.
"""

AUTH_PROPOSAL_TEMPLATE = """
# Propuesta de Implementación: {functionality}

## Descripción
{description}

## Mecanismo de autenticación
{auth_mechanism}

## Archivos a crear/modificar
{files_section}

## Estructura sugerida
{structure_section}

## Elementos de seguridad a implementar
- Gestión segura de contraseñas (hashing con bcrypt/Argon2)
- Protección contra ataques de fuerza bruta
- Implementación de tokens JWT o similares
- Almacenamiento seguro de secretos
- Manejo adecuado de sesiones
- Validaciones robustas de entrada
- Protección contra CSRF
{security_elements}

## Patrones y buenas prácticas
{patterns_section}

## Estimación de complejidad
{complexity_section}

## Consideraciones adicionales
- Implementar autenticación multifactor (MFA) 
- Gestión de permisos y roles de usuario
- Registro de eventos de seguridad (logs)
- Mecanismo de recuperación de contraseñas
- Validación de emails

## Pasos de implementación recomendados
1. Implementar modelo de usuario y persistencia
2. Desarrollar endpoints/rutas de autenticación básica
3. Añadir mecanismos de hashing y seguridad
4. Implementar gestión de tokens/sesiones
5. Desarrollar sistema de permisos y roles
6. Añadir características avanzadas (MFA, etc.)
7. Implementar tests de seguridad

---
*Generado automáticamente por ProjectPrompt*
"""
