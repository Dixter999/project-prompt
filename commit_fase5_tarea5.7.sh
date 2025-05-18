#!/bin/bash
# Script para hacer commit de la implementación de Fase 5, tarea 5.7

# Definir mensaje de commit
COMMIT_MSG="Fase 5, Tarea 5.7: Implementación de comandos premium en CLI

Se implementaron los siguientes comandos premium:
- project-prompt premium dashboard: Dashboard interactivo con métricas avanzadas
- project-prompt premium test-generator: Generador de tests unitarios
- project-prompt premium verify-completeness: Verificador de completitud
- project-prompt premium implementation: Asistente de implementación detallado

Se añadió el submenu de suscripción:
- project-prompt subscription info: Información sobre suscripción
- project-prompt subscription activate: Activar licencia
- project-prompt subscription deactivate: Desactivar licencia
- project-prompt subscription plans: Ver planes disponibles

Tareas completadas:
- Integración con sistema de verificación de suscripción
- Comprobación de características premium disponibles
- Sugerencia de actualización a premium
- Actualización de documentación

Issue: Fase 5, tarea 5.7
Branch: feature/premium-cli-commands"

# Añadir cambios
git add src/main.py
git add fases/fase5_progress.md
git add commit_fase5_tarea5.7.sh

# Hacer commit
git commit -m "$COMMIT_MSG"

# Recordatorio para hacer push
echo "Commit creado exitosamente."
echo "Para subir los cambios al repositorio remoto, ejecuta:"
echo "git push origin feature/premium-cli-commands"
