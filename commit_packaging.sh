#!/bin/bash

# Script para realizar commit de la implementación del sistema de empaquetado y distribución
# Tarea 6.6: "Empaquetado y distribución"

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Creando commit para la tarea 6.6: Empaquetado y distribución${NC}"

# Asegurar que estamos en la rama feature/packaging
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/packaging" ]; then
    echo -e "${YELLOW}Cambiando a la rama feature/packaging${NC}"
    git checkout feature/packaging || { echo "Error al cambiar de rama"; exit 1; }
fi

# Mostrar los archivos modificados y nuevos
echo -e "${YELLOW}Archivos modificados y nuevos:${NC}"
git status --short

# Agregar los archivos al staging
echo -e "${YELLOW}Agregando archivos al staging...${NC}"
git add pyproject.toml
git add setup.py
git add setup.cfg
git add requirements.txt
git add MANIFEST.in
git add scripts/build.py
git add scripts/test_package.py
git add .github/workflows/release.yml
git add src/__init__.py
git add fases/fase6_progress.md

# Verificar si hay más archivos que agregar
echo -e "${YELLOW}¿Hay más archivos que agregar al commit? [y/N]:${NC}"
read ADD_MORE
if [[ $ADD_MORE == "y" || $ADD_MORE == "Y" ]]; then
    git add -i
fi

# Mostrar el resumen de cambios
echo -e "${YELLOW}Resumen de cambios a commitear:${NC}"
git status

# Confirmar antes de hacer commit
echo -e "${YELLOW}¿Proceder con el commit? [Y/n]:${NC}"
read CONFIRM
if [[ $CONFIRM == "n" || $CONFIRM == "N" ]]; then
    echo "Operación cancelada"
    exit 0
fi

# Realizar el commit
git commit -m "Feat: Implementa sistema de empaquetado y distribución (Tarea 6.6)

- Actualiza pyproject.toml con metadata completa y configuración para Poetry
- Actualiza setup.py y agrega setup.cfg para compatibilidad con setuptools
- Crea MANIFEST.in para control de archivos incluidos en el paquete
- Crea scripts de construcción para paquetes Python y ejecutables
- Configura workflow de GitHub para automatizar releases
- Prepara sistema para distribución en PyPI y VS Code Marketplace
- Actualiza versión a 1.0.0 para release estable
- Actualiza fase6_progress.md para marcar la tarea como completada"

# Mostrar el resultado
echo -e "${GREEN}Commit realizado exitosamente${NC}"
echo -e "${YELLOW}¿Desea hacer push de los cambios? [y/N]:${NC}"
read DO_PUSH
if [[ $DO_PUSH == "y" || $DO_PUSH == "Y" ]]; then
    git push origin feature/packaging
    echo -e "${GREEN}Push realizado exitosamente${NC}"
fi

echo -e "${GREEN}Tarea 6.6 'Empaquetado y distribución' completada y commiteada${NC}"
