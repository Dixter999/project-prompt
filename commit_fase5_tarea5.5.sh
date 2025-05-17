#!/bin/bash

# Script para commit de la tarea 5.5 - Integración con Copilot y Anthropic

echo "Preparando commit para la tarea 5.5 - Integración con Copilot y Anthropic..."

# Asegurar que estamos en el branch correcto
CURRENT_BRANCH=$(git branch --show-current)
TARGET_BRANCH="feature/ai-integrations"

if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
    echo "Error: No estás en el branch $TARGET_BRANCH"
    echo "Por favor, cambia al branch correcto con: git checkout $TARGET_BRANCH"
    exit 1
fi

# Archivos a incluir en el commit
git add src/integrations/anthropic_advanced.py
git add src/integrations/copilot_advanced.py
git add src/utils/prompt_optimizer.py
git add src/integrations/__init__.py
git add src/main.py
git add tests/test_ai_integrations.py
git add fases/fase5_progress.md

# Mensaje de commit
COMMIT_MSG="feat(ai-integrations): Implementación de integraciones avanzadas con IA

Tarea 5.5 - Integración con Copilot y Anthropic:
- Implementación de cliente avanzado para Anthropic con capacidades premium
- Implementación de cliente avanzado para GitHub Copilot con capacidades premium
- Creación de optimizador de prompts para mejorar resultados de IA
- Funcionalidades premium para generación de código, detección de errores y refactorización
- Comandos CLI para acceder a capacidades de IA avanzada
- Tests unitarios para asegurar el funcionamiento correcto
- Actualización de fase5_progress.md

Esta mejora permite a los usuarios premium aprovechar capacidades avanzadas
de las APIs de IA para mejorar la calidad del código y la productividad."

# Realizar commit
git commit -m "$COMMIT_MSG"

echo "Commit realizado exitosamente."
echo "Para subir los cambios al repositorio remoto, ejecuta: git push origin $TARGET_BRANCH"
