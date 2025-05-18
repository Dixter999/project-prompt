#!/bin/bash

# Script para realizar commit de la implementación del sistema de telemetría anónima
# Tarea 6.5: "Sistema de telemetría anónima"

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Creando commit para la tarea 6.5: Sistema de telemetría anónima${NC}"

# Asegurar que estamos en la rama feature/anonymous-telemetry
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/anonymous-telemetry" ]; then
    echo -e "${YELLOW}Cambiando a la rama feature/anonymous-telemetry${NC}"
    git checkout feature/anonymous-telemetry || { echo "Error al cambiar de rama"; exit 1; }
fi

# Mostrar los archivos modificados y nuevos
echo -e "${YELLOW}Archivos modificados y nuevos:${NC}"
git status --short

# Agregar los archivos al staging
echo -e "${YELLOW}Agregando archivos al staging...${NC}"
git add src/utils/telemetry.py
git add src/ui/consent_manager.py
git add src/main.py
git add fases/fase6_progress.md
git add tests/test_telemetry.py 2>/dev/null || echo -e "${YELLOW}Nota: No se encontró archivo de test de telemetría${NC}"

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
git commit -m "Feat: Implementa sistema de telemetría anónima (Tarea 6.5)

- Añade sistema de telemetría anónima en src/utils/telemetry.py
- Implementa gestor de consentimiento en src/ui/consent_manager.py 
- Agrega comandos de telemetría en main.py
- Incluye mecanismo de generación de ID anónimo
- Añade decorador para captura de uso de comandos y errores
- Implementa sistema de opt-in con transparencia en datos recolectados
- Actualiza fase6_progress.md para marcar la tarea como completada"

# Mostrar el resultado
echo -e "${GREEN}Commit realizado exitosamente${NC}"
echo -e "${YELLOW}¿Desea hacer push de los cambios? [y/N]:${NC}"
read DO_PUSH
if [[ $DO_PUSH == "y" || $DO_PUSH == "Y" ]]; then
    git push origin feature/anonymous-telemetry
    echo -e "${GREEN}Push realizado exitosamente${NC}"
fi

echo -e "${GREEN}Tarea 6.5 'Sistema de telemetría anónima' completada y commiteada${NC}"
