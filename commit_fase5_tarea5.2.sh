#!/bin/bash
# Comando para hacer commit de la tarea 5.2 de la fase 5

# Asegurarse de estar en la rama correcta
git checkout feature/implementation-prompts

# Añadir todos los archivos modificados
git add src/templates/premium/implementation_steps.md
git add src/templates/premium/premium_templates.py
git add src/generators/implementation_prompt_generator.py
git add src/generators/__init__.py
git add src/main.py
git add fases/fase5_progress.md

# Hacer commit con mensaje descriptivo
git commit -m "Implementación de la tarea 5.2: Generación de prompts para implementación

- Creado sistema de generación de prompts específicos para implementación
- Implementados templates premium con patrones de código y arquitectura
- Añadido generador de prompts de implementación con soporte premium
- Verificación de suscripción premium integrada
- Añadidos comandos CLI para acceder a las funcionalidades"

echo "Commit realizado. Continúa en la rama feature/implementation-prompts"
