#!/bin/bash

# Script para preparar commit de la tarea 4.4: Generación de propuestas de implementación

echo "Preparando commit para la fase 4, tarea 4.4: Generación de propuestas de implementación"

# Asegurar que estamos en el branch correcto
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/implementation-proposals" ]; then
    echo "ERROR: No estás en el branch feature/implementation-proposals"
    echo "Ejecuta: git checkout feature/implementation-proposals"
    exit 1
fi

# Agregar archivos modificados
git add src/templates/proposals/
git add src/generators/implementation_proposal_generator.py
git add src/main.py
git add fases/fase4_progress.md

# Realizar el commit
git commit -m "Implementada generación de propuestas de implementación (Fase 4, tarea 4.4)

* Creado generador de propuestas de implementación para funcionalidades
* Implementadas plantillas especializadas para diferentes tipos de funcionalidades:
  - Plantilla genérica con formato estándar
  - Plantilla específica para autenticación
  - Plantilla específica para bases de datos
* Integrado comando CLI implementation-proposal
* Actualizado archivo de progreso de la fase 4

Refs: fase4, tarea 4.4"

echo "Commit realizado. Ahora puedes hacer git push con:"
echo "git push origin feature/implementation-proposals"
