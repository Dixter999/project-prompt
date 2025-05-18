#!/bin/zsh
# Script para hacer commit de la corrección del error de importación

# Configurar variables
BRANCH_NAME="feature/update-system"
COMMIT_MESSAGE="Corrige error de importación en el sistema de actualización y sincronización"
DESCRIPTION="
- Corrige ImportError al importar Config desde src.utils.config
- Reemplaza la importación de Config por ConfigManager y get_config
- Actualiza los constructores en updater.py y sync_manager.py
- Corrige los tests para usar la implementación correcta
"

# Verificar rama actual
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]]; then
  echo "Error: No estás en la rama $BRANCH_NAME"
  exit 1
fi

# Mostrar cambios realizados
echo "Mostrando cambios en los archivos afectados..."
git diff src/utils/updater.py src/utils/sync_manager.py tests/test_updater.py tests/test_sync_manager.py

# Confirmar al usuario
echo "\n¿Desea realizar el commit con el siguiente mensaje?\n"
echo "$COMMIT_MESSAGE\n$DESCRIPTION"
echo "\n¿Continuar? [y/N]"
read CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Commit cancelado"
  exit 1
fi

# Realizar commit
git add src/utils/updater.py src/utils/sync_manager.py tests/test_updater.py tests/test_sync_manager.py
git commit -m "$COMMIT_MESSAGE" -m "$DESCRIPTION"

echo "\nCommit realizado con éxito en la rama $BRANCH_NAME"
echo "Para subir los cambios, ejecute: git push origin $BRANCH_NAME"
