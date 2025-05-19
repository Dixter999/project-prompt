#!/usr/bin/env bash
# restructure_project.sh
#
# Script para reorganizar la estructura del proyecto ProjectPrompt
# siguiendo las recomendaciones del análisis de estructura

set -e  # Salir en caso de error

# Colores para mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin Color

# Verificar si estamos en el directorio raíz del proyecto
if [ ! -f "project_prompt.py" ] || [ ! -d "src" ]; then
    echo -e "${RED}Este script debe ejecutarse desde el directorio raíz del proyecto ProjectPrompt.${NC}"
    exit 1
fi

echo -e "${BLUE}=== Reorganización de Estructura del Proyecto ===${NC}"
echo -e "${BLUE}=================================================${NC}\n"

# Determinar si es un ensayo o ejecución real
DRY_RUN=true
if [[ "$1" == "--execute" ]]; then
    DRY_RUN=false
    echo -e "${YELLOW}EJECUCIÓN REAL: Los cambios se aplicarán al proyecto.${NC}"
else
    echo -e "${GREEN}ENSAYO: No se realizarán cambios. Use --execute para aplicar cambios.${NC}"
fi

# Función para crear directorios si no existen
create_dir() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${BLUE}Crearía directorio: $1${NC}"
    else
        if [ ! -d "$1" ]; then
            mkdir -p "$1"
            echo -e "  ${GREEN}Creado directorio: $1${NC}"
        else
            echo -e "  ${YELLOW}El directorio ya existe: $1${NC}"
        fi
    fi
}

# Función para mover archivos
move_file() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${BLUE}Movería: $1 -> $2${NC}"
    else
        if [ -f "$1" ]; then
            # Crear el directorio destino si no existe
            mkdir -p "$(dirname "$2")"
            
            # Mover el archivo
            mv "$1" "$2"
            echo -e "  ${GREEN}Movido: $1 -> $2${NC}"
        else
            echo -e "  ${RED}No se encontró el archivo: $1${NC}"
        fi
    fi
}

echo -e "\n${YELLOW}1. Creando estructura de directorios mejorada...${NC}"

# Crear directorios para la estructura mejorada
create_dir "tools/scripts"
create_dir "tools/ci"
create_dir "tools/utils"
create_dir "docs/development"
create_dir "docs/api"
create_dir "docs/user"
create_dir "bin"

echo -e "\n${YELLOW}2. Reorganizando scripts de shell...${NC}"

# Mover scripts de shell al directorio tools/scripts
if [ "$DRY_RUN" = false ]; then
    find . -maxdepth 1 -name "*.sh" -type f | while read -r script; do
        # Excluir scripts especiales que deberían permanecer en la raíz
        if [[ "$script" != "./setup_environment.sh" ]]; then
            basename_script=$(basename "$script")
            move_file "$script" "tools/scripts/$basename_script"
            
            # Crear un enlace simbólico para mantener la compatibilidad
            ln -sf "tools/scripts/$basename_script" "$basename_script"
            echo -e "  ${GREEN}Creado enlace simbólico: $basename_script -> tools/scripts/$basename_script${NC}"
        else
            echo -e "  ${YELLOW}Manteniendo en la raíz: $script${NC}"
        fi
    done
else
    find . -maxdepth 1 -name "*.sh" -type f | while read -r script; do
        if [[ "$script" != "./setup_environment.sh" ]]; then
            basename_script=$(basename "$script")
            echo -e "  ${BLUE}Movería: $script -> tools/scripts/$basename_script${NC}"
            echo -e "  ${BLUE}Crearía enlace simbólico: $basename_script -> tools/scripts/$basename_script${NC}"
        else
            echo -e "  ${YELLOW}Mantendría en la raíz: $script${NC}"
        fi
    done
fi

echo -e "\n${YELLOW}3. Reorganizando scripts de prueba...${NC}"

# Mover scripts de prueba al directorio tools/scripts
if [ "$DRY_RUN" = false ]; then
    for test_script in test_*.py test_*.sh; do
        if [ -f "$test_script" ] && [[ "$test_script" != "test_projectprompt.sh" ]]; then
            move_file "$test_script" "tools/scripts/$test_script"
        fi
    done
else
    for test_script in test_*.py test_*.sh; do
        if [ -f "$test_script" ] && [[ "$test_script" != "test_projectprompt.sh" ]]; then
            echo -e "  ${BLUE}Movería: $test_script -> tools/scripts/$test_script${NC}"
        fi
    done
fi

echo -e "\n${YELLOW}4. Reorganizando scripts de utilidad...${NC}"

# Lista de scripts de utilidad para mover
UTILITY_SCRIPTS=("fix_config_in_telemetry.py" "set_anthropic_key.py" "structure_improvement.py" "verify_freemium_system.py")

for script in "${UTILITY_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        move_file "$script" "tools/utils/$script"
    fi
done

echo -e "\n${YELLOW}5. Reorganizando documentación...${NC}"

# Mover archivos de fases a documentación de desarrollo
if [ "$DRY_RUN" = false ]; then
    if [ -d "fases" ]; then
        mkdir -p "docs/development/fases"
        find "fases" -name "*.md" -type f | while read -r file; do
            basename_file=$(basename "$file")
            move_file "$file" "docs/development/fases/$basename_file"
        done
        rmdir "fases" 2>/dev/null || true
        echo -e "  ${GREEN}Eliminado directorio: fases${NC}"
    fi
else
    if [ -d "fases" ]; then
        echo -e "  ${BLUE}Movería contenido de fases/ a docs/development/fases/${NC}"
        echo -e "  ${BLUE}Eliminaría directorio: fases${NC}"
    fi
fi

echo -e "\n${YELLOW}6. Limpiando directorios vacíos...${NC}"

# Limpiar directorios vacíos
if [ "$DRY_RUN" = false ]; then
    # Buscar directorios vacíos y eliminarlos
    find . -type d -empty | grep -v '\.git' | while read -r dir; do
        rmdir "$dir" 2>/dev/null || true
        echo -e "  ${GREEN}Eliminado directorio vacío: $dir${NC}"
    done
else
    find . -type d -empty | grep -v '\.git' | while read -r dir; do
        echo -e "  ${BLUE}Eliminaría directorio vacío: $dir${NC}"
    done
fi

echo -e "\n${YELLOW}7. Creando enlaces simbólicos en bin/ para comandos principales...${NC}"

# Crear enlaces simbólicos en bin para los comandos principales
if [ "$DRY_RUN" = false ]; then
    ln -sf "../project_prompt.py" "bin/project-prompt"
    chmod +x "bin/project-prompt"
    echo -e "  ${GREEN}Creado enlace simbólico: bin/project-prompt -> ../project_prompt.py${NC}"
    
    ln -sf "../quick_analyze.py" "bin/quick-analyze"
    chmod +x "bin/quick-analyze"
    echo -e "  ${GREEN}Creado enlace simbólico: bin/quick-analyze -> ../quick_analyze.py${NC}"
    
    ln -sf "../simple_analyze.py" "bin/simple-analyze"
    chmod +x "bin/simple-analyze"
    echo -e "  ${GREEN}Creado enlace simbólico: bin/simple-analyze -> ../simple_analyze.py${NC}"
else
    echo -e "  ${BLUE}Crearía enlaces simbólicos en bin/ para comandos principales${NC}"
fi

echo -e "\n${YELLOW}8. Eliminando archivos pyc y directorios __pycache__...${NC}"

# Eliminar archivos .pyc y directorios __pycache__
if [ "$DRY_RUN" = false ]; then
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +
    echo -e "  ${GREEN}Eliminados archivos .pyc y directorios __pycache__${NC}"
else
    echo -e "  ${BLUE}Eliminaría archivos .pyc y directorios __pycache__${NC}"
fi

echo -e "\n${GREEN}=== Proceso completado ===${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Este fue un ensayo. Ejecute con --execute para aplicar los cambios.${NC}"
    echo -e "${YELLOW}Comando: ./restructure_project.sh --execute${NC}"
else
    echo -e "${GREEN}La estructura del proyecto ha sido reorganizada con éxito.${NC}"
    echo -e "${YELLOW}Nota: Puede ser necesario actualizar rutas en scripts o importaciones.${NC}"
fi
