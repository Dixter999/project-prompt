#!/bin/zsh
# Script para realizar commit de la Fase 6, tarea 6.4: Documentación completa

# Configurar variables
BRANCH_NAME="feature/complete-documentation"
COMMIT_MESSAGE="Fase 6, tarea 6.4: Documentación completa"
DESCRIPTION="
- Creación de estructura completa de documentación
- Documentación para usuarios: guías, tutoriales y referencias
- Documentación para desarrolladores: arquitectura, contribución y diseño
- Documentación de la API: referencia técnica y ejemplos de uso
- Página principal de documentación y organización por secciones
- Actualización del archivo de progreso de fase
"

# Verificar que estamos en el directorio correcto
if [[ ! -d "docs" ]]; then
  echo "Error: Este script debe ejecutarse desde el directorio raíz del proyecto"
  exit 1
fi

# Verificar rama actual
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]]; then
  # Verificar si la rama existe
  if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    git checkout $BRANCH_NAME
  else
    # Crear y cambiar a la rama
    git checkout -b $BRANCH_NAME feature/enhanced-cli-ux
  fi
fi

# Verificar cambios
echo "Mostrando cambios en la documentación..."
git status docs/

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
git add docs/
git add fases/fase6_progress.md
git commit -m "$COMMIT_MESSAGE" -m "$DESCRIPTION"

echo "\nCommit realizado con éxito en la rama $BRANCH_NAME"
echo "Para subir los cambios, ejecute: git push origin $BRANCH_NAME"
