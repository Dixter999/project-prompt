#!/bin/bash

# Script para commit de la tarea 5.4 - Verificador de completitud

echo "Preparando commit para la tarea 5.4 - Verificador de completitud..."

# Asegurar que estamos en el branch correcto
CURRENT_BRANCH=$(git branch --show-current)
TARGET_BRANCH="feature/completeness-verifier"

if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
    echo "Error: No estás en el branch $TARGET_BRANCH"
    echo "Por favor, cambia al branch correcto con: git checkout $TARGET_BRANCH"
    exit 1
fi

# Archivos a incluir en el commit
git add src/analyzers/completeness_verifier.py
git add src/analyzers/__init__.py
git add src/templates/verification/templates.json
git add src/templates/verification/checklists.json
git add src/main.py
git add fases/fase5_progress.md

# Mensaje de commit
COMMIT_MSG="feat(completeness-verifier): Implementación del verificador de completitud

Tarea 5.4 - Verificador de completitud:
- Implementación de la clase CompletenessVerifier
- Creación de plantillas y checklists de verificación
- Actualización de __init__.py para incluir el nuevo verificador
- Adición de comando CLI para verificar completitud
- Actualización de fase5_progress.md

Este verificador permite analizar el nivel de completitud de implementaciones
de funcionalidades según criterios predefinidos y genera sugerencias de mejora."

# Realizar commit
git commit -m "$COMMIT_MSG"

echo "Commit realizado exitosamente."
echo "Para subir los cambios al repositorio remoto, ejecuta: git push origin $TARGET_BRANCH"
