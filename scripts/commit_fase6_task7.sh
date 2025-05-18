#!/bin/bash

# Script to commit changes for Fase 6, Tarea 6.7: "Pruebas finales e integración"

# Verify we are in the correct branch
CURRENT_BRANCH=$(git branch --show-current)
EXPECTED_BRANCH="feature/final-testing"

if [ "$CURRENT_BRANCH" != "$EXPECTED_BRANCH" ]; then
  echo "Error: You are on branch $CURRENT_BRANCH but should be on $EXPECTED_BRANCH"
  echo "Please switch to the correct branch with: git checkout $EXPECTED_BRANCH"
  exit 1
fi

# Add all files related to this task
git add tests/integration/__init__.py
git add tests/integration/test_project_analysis.py
git add tests/integration/test_prompt_generation.py
git add tests/integration/test_ai_integration.py
git add tests/e2e/__init__.py
git add tests/e2e/test_main_workflow.py
git add tests/e2e/test_cli_commands.py
git add tests/e2e/test_vscode_extension.py
git add scripts/run_tests.py
git add scripts/optimize_performance.py
git add scripts/fix_bugs.py
git add fases/fase6_progress.md
git add scripts/commit_fase6_task7.sh

# Commit the changes
git commit -m "Fase 6, Tarea 6.7: Implementadas pruebas finales e integración

- Creadas pruebas de integración para verificar interacciones entre componentes
- Creadas pruebas e2e que simulan flujos de trabajo reales
- Implementados scripts de prueba para CI/CD en diferentes sistemas operativos
- Añadidas herramientas de optimización de rendimiento
- Añadidas utilidades de corrección automática de errores
- Actualizado fase6_progress.md para marcar la tarea como completada"

echo "Cambios para la Tarea 6.7 'Pruebas finales e integración' commits correctamente"
echo "Para subir los cambios al repositorio remoto, ejecuta: git push origin $EXPECTED_BRANCH"
