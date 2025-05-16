#!/bin/bash

# Script de commit para la tarea 4.6 de la Fase 4
# Comandos en CLI para análisis específicos

echo "Realizando commit para la tarea 4.6 (Comandos en CLI para análisis específicos)"

# Mensaje de commit
MENSAJE="feat(cli): implementar comandos para análisis específicos

Integración de comandos para análisis de funcionalidades específicas en CLI:
- project-prompt analyze-feature [name]
- project-prompt interview [name] 
- project-prompt suggest-branches

Parte de la tarea 4.6 de la Fase 4"

# Agregar archivos modificados
git add src/ui/cli.py fases/fase4_progress.md

# Realizar commit
git commit -m "$MENSAJE"

echo "Commit realizado con éxito"
