#!/bin/bash
# Script para confirmar los cambios de la Fase 6, Tarea 6.3: Mejoras de UX para CLI

# Asegurar que estamos en la rama correcta
git checkout feature/enhanced-cli-ux || exit 1

# Agregar los archivos nuevos y modificados
git add src/ui/wizards/
git add src/ui/themes.py
git add src/ui/cli.py
git add src/ui/menu.py
git add fases/fase6_progress.md

# Crear el commit con mensaje descriptivo
git commit -m "Fase 6, Tarea 6.3: Mejoras de UX para CLI

Implementado:
- Sistema de wizards interactivos para guiar al usuario
- Sistema de temas con múltiples esquemas de colores
- Visualización mejorada con Rich (tablas, paneles, markdown)
- Spinners y barras de progreso para operaciones largas
- Resaltado de código y visualización de resultados
- Manejo mejorado de entrada con autocompletado
- Gestión de layouts y organización de pantalla
- Secciones en menús y soporte para submenús

Resolví el problema de importación circular entre themes.py y config.py
mediante el uso de importaciones perezosas (lazy imports)."

echo "Commit creado exitosamente. Puedes hacer push con: git push origin feature/enhanced-cli-ux"
