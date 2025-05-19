#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plantilla especializada para propuestas de implementación de bases de datos.
"""

DATABASE_PROPOSAL_TEMPLATE = """
# Propuesta de Implementación: {functionality}

## Descripción
{description}

## Tipo de Base de Datos
{db_type}

## Archivos a crear/modificar
{files_section}

## Estructura de datos propuesta
{data_structure}

## Esquema de entidades y relaciones
{schema_section}

## Operaciones principales a implementar
- Create: inserción de nuevos registros
- Read: consulta y filtrado de datos
- Update: actualización de registros existentes
- Delete: eliminación segura de registros
- Relaciones: manejo de JOINs/referencias entre entidades
- Indexación: para consultas de alto rendimiento
{operations_section}

## Patrones y buenas prácticas
- Uso de ORM/ODM para mapeo objeto-relacional
- Transacciones para operaciones críticas
- Prepared statements para prevenir inyecciones
- Conexiones seguras y manejo de credenciales
- Optimización de consultas y uso de índices
- Migración y versionado de esquemas
{patterns_section}

## Estimación de complejidad
{complexity_section}

## Consideraciones adicionales
- Escalabilidad: estrategias de partición/sharding si es necesario
- Respaldo: planificación de copias de seguridad
- Monitoreo: métricas de rendimiento y alertas
- Seguridad: cifrado de datos sensibles

## Pasos de implementación recomendados
1. Definir el esquema de datos y relaciones
2. Configurar conexión a la base de datos
3. Implementar modelos y migraciones iniciales
4. Desarrollar capa de acceso a datos (DAO/Repository)
5. Implementar operaciones CRUD básicas
6. Añadir índices y optimizaciones
7. Desarrollar pruebas de integración

---
*Generado automáticamente por ProjectPrompt*
"""
