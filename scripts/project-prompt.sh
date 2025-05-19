#!/usr/bin/env bash

# Wrapper para el analizador de proyectos
# Este script facilita el uso del analizador de proyectos

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function show_help() {
  echo "ProjectPrompt - Analizador de proyectos"
  echo ""
  echo "Uso:"
  echo "  project-prompt.sh [comando] [opciones]"
  echo ""
  echo "Comandos:"
  echo "  analyze [ruta]       Analizar un proyecto"
  echo "  init                 Inicializar un nuevo proyecto"
  echo "  help                 Mostrar esta ayuda"
  echo ""
  echo "Para analizar un proyecto:"
  echo "  project-prompt.sh analyze /ruta/a/tu/proyecto [archivo-salida.json]"
  echo ""
  echo "Ejemplos:"
  echo "  project-prompt.sh analyze ."
  echo "  project-prompt.sh analyze /ruta/a/proyecto resultado.json"
}

function analyze() {
  local PROJECT_PATH="$1"
  local OUTPUT_FILE="$2"
  
  if [ -z "$PROJECT_PATH" ]; then
    PROJECT_PATH="."
  fi
  
  if [ -n "$OUTPUT_FILE" ]; then
    python "$SCRIPT_DIR/project_analyzer.py" "$PROJECT_PATH" "$OUTPUT_FILE"
  else
    python "$SCRIPT_DIR/project_analyzer.py" "$PROJECT_PATH"
  fi
}

function init() {
  echo "Inicializando nuevo proyecto..."
  echo "Esta función está pendiente de implementación."
}

case "$1" in
  analyze)
    analyze "$2" "$3"
    ;;
  init)
    init
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    if [ -z "$1" ]; then
      show_help
    else
      echo "Comando desconocido: $1"
      echo ""
      show_help
      exit 1
    fi
    ;;
esac
