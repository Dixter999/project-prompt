#!/bin/zsh
# Script para realizar commit de la Fase 6, tarea 6.1: Extensión para VSCode

# Configurar variables
BRANCH_NAME="feature/vscode-extension"
COMMIT_MESSAGE="Fase 6, tarea 6.1: Implementación de extensión para VSCode"
DESCRIPTION="
- Creación de la estructura base de la extensión para VSCode
- Implementación de panel interactivo con pestañas
- Integración con la paleta de comandos
- Vista de árbol para funcionalidades, documentación y prompts
- Integración con GitHub Copilot
- Estilos adaptados al tema de VSCode
- Implementación de comandos para análisis de proyecto y generación de prompts
"

# Verificar que estamos en el directorio correcto
if [[ ! -d "vscode-extension" ]]; then
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
    git checkout -b $BRANCH_NAME feature/premium-cli-commands
  fi
fi

# Verificar cambios
echo "Mostrando cambios en la extensión VS Code..."
git status vscode-extension/

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
git add vscode-extension/
git add fases/fase6_progress.md
git commit -m "$COMMIT_MESSAGE" -m "$DESCRIPTION"

echo "\nCommit realizado con éxito en la rama $BRANCH_NAME"
echo "Para subir los cambios, ejecute: git push origin $BRANCH_NAME"
