#!/bin/bash
# Script para realizar el commit de la tarea 5.3: Generador de tests unitarios

echo "Realizando commit de la tarea 5.3: Generador de tests unitarios"

git add src/generators/test_generator.py
git add src/templates/tests/
git add src/analyzers/testability_analyzer.py
git add src/analyzers/__init__.py
git add src/generators/__init__.py
git add src/main.py
git add fases/fase5_progress.md

git commit -m "Implementación de la tarea 5.3: Generador de tests unitarios

- Creado TestGenerator para generar tests unitarios para proyectos
- Implementado TestabilityAnalyzer para analizar la testabilidad del código
- Añadidas plantillas para la generación de tests
- Integrado en CLI con el comando generate-tests
- Funcionalidad para generar tests por archivo o funcionalidad
- Soporte para detectar el framework de tests del proyecto (pytest/unittest)
- Actualizado el progreso en fase5_progress.md"

echo "Commit completado"
