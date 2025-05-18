#!/bin/bash
# Script para commit de la tarea 5.6 - Dashboard de progreso del proyecto

# Mensaje de commit
echo "Implementado Dashboard de progreso del proyecto (Tarea 5.6)

- Creado ProjectProgressTracker para analizar y seguir progreso
- Implementado DashboardGenerator para visualización HTML
- Añadido soporte para versiones premium y free
- Implementadas métricas de completitud, calidad y testing
- Integrado con CLI principal con comando 'dashboard'
- Creados tests unitarios para validación

Parte de la Fase 5: Implementación de Funcionalidades Premium" > commit_message.txt

# Añadir archivos
git add src/analyzers/project_progress_tracker.py
git add src/ui/dashboard.py
git add tests/test_dashboard.py
git add src/main.py
git add fases/fase5_progress.md
git add commit_fase5_tarea5.6.sh

# Realizar commit usando el mensaje
git commit -F commit_message.txt

# Mostrar mensaje de confirmación
echo "Commit de la tarea 5.6 realizado correctamente"
