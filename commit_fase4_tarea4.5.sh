#!/bin/bash
# Script para realizar commit de la tarea 4.5 de la fase 4

# Generar mensaje de commit detallado
cat > commit_message.txt << EOL
feat(branch-suggestions): Implementar sugerencias de estructura de branches

- Añadir generador de estrategias de branches en src/generators/branch_strategy_generator.py
- Crear plantillas de branches y workflows en src/templates/git/branch_templates.py
- Implementar comando CLI 'suggest-branches' para generar estrategias de branches
- Añadir detección automática de dependencias entre funcionalidades
- Integrar con propuestas de implementación existentes
- Actualizar archivo de progreso fase4_progress.md

Parte de la Fase 4, Tarea 4.5
EOL

# Añadir archivos modificados
git add src/generators/branch_strategy_generator.py
git add src/templates/git/__init__.py
git add src/templates/git/branch_templates.py
git add src/main.py
git add fases/fase4_progress.md
git add commit_fase4_tarea4.5.sh

# Realizar commit con el mensaje generado
git commit -F commit_message.txt

echo "✅ Commit realizado correctamente para la tarea 4.5 (Sugerencias de estructura de branches)"
