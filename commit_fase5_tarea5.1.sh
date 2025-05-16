#!/bin/bash

# Script para realizar el commit de la tarea 5.1: Sistema de verificación de subscripción

echo "Realizando commit de la tarea 5.1: Sistema de verificación de subscripción..."

# Añadir archivos modificados
git add src/utils/license_validator.py
git add src/utils/subscription_manager.py
git add src/ui/subscription_view.py
git add src/utils/__init__.py
git add src/main.py
git add fases/fase5_progress.md

# Realizar commit
git commit -m "feat(subscription): Implementa sistema de verificación de subscripción (Fase 5, Tarea 5.1)

- Añade validador de licencias con soporte offline/online
- Implementa gestor de subscripciones con límites por tipo
- Añade vista para gestionar subscripciones desde CLI
- Integra comandos CLI para gestión de subscripción
- Actualiza documentación de progreso"

echo "Commit completado. Puedes hacer push con: git push origin feature/subscription-verification"
