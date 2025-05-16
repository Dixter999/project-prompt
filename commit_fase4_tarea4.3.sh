#!/bin/bash

echo "Preparando commit para la fase 4, tarea 4.3: Sistema de entrevistas guiadas"

# Asegurar que estamos en el branch correcto
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/guided-interviews" ]; then
    echo "ERROR: No estás en el branch feature/guided-interviews"
    echo "Ejecuta: git checkout feature/guided-interviews"
    exit 1
fi

# Agregar archivos modificados
git add src/ui/interview_system.py
git add src/ui/__init__.py
git add src/templates/interviews/
git add src/main.py
git add fases/fase4_progress.md

# Realizar el commit
git commit -m "Implementado sistema de entrevistas guiadas (Fase 4, tarea 4.3)

* Creado sistema de entrevistas para clarificar funcionalidades poco claras
* Implementada clase InterviewSystem con capacidad para entrevistas adaptativas
* Creadas plantillas de preguntas genéricas y específicas para APIs
* Implementado guardado de respuestas en formato JSON y Markdown
* Integrada funcionalidad con comandos CLI: interview y list-interviews
* Actualizado archivo de progreso de la fase 4

Refs: fase4, tarea 4.3"

echo "Commit realizado. Ahora puedes hacer git push con:"
echo "git push origin feature/guided-interviews"
