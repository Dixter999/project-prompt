#!/usr/bin/env bash
# Script para verificación final y despliegue de ProjectPrompt
# Esta versión es el script de verificación completa previo a la publicación

set -e  # Detener en caso de error

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin Color

# Imprimir banner
echo -e "${BLUE}"
echo "=================================================================="
echo "     ProjectPrompt - Verificación Final y Preparación de Release"
echo "=================================================================="
echo -e "${NC}"

# Directorio base del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ------------------------------------------------------------
# SECCIÓN 1: Verificación de entorno y dependencias
# ------------------------------------------------------------
echo -e "\n${YELLOW}[1/7] Verificando entorno y dependencias...${NC}"

# Verificar Python
python_version=$(python3 --version 2>&1)
if [[ $python_version =~ Python\ 3\.[0-9]+\.[0-9]+ ]]; then
    echo -e "✓ ${GREEN}Python detectado: $python_version${NC}"
else
    echo -e "✗ ${RED}Python 3.x no encontrado. Por favor instale Python 3.8 o superior.${NC}"
    exit 1
fi

# Verificar dependencias
echo -e "Verificando dependencias de Python..."
missing_deps=0

check_dependency() {
    local pkg=$1
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "✓ ${GREEN}$pkg instalado${NC}"
        return 0
    else
        echo -e "✗ ${RED}$pkg no encontrado${NC}"
        return 1
    fi
}

# Lista de dependencias críticas
deps=("json" "pathlib" "requests" "setuptools" "argparse")
for dep in "${deps[@]}"; do
    check_dependency "$dep" || ((missing_deps++))
done

if [ $missing_deps -gt 0 ]; then
    echo -e "\n${RED}[ERROR] Faltan $missing_deps dependencias. Instálelas con:${NC}"
    echo -e "pip install -r requirements.txt"
    exit 1
else
    echo -e "${GREEN}Todas las dependencias básicas están instaladas.${NC}"
fi

# ------------------------------------------------------------
# SECCIÓN 2: Verificación de estructura del proyecto
# ------------------------------------------------------------
echo -e "\n${YELLOW}[2/7] Verificando estructura del proyecto...${NC}"

# Verificar archivos críticos
critical_files=(
    "project_prompt.py"
    "project_prompt_cli.py"
    "project_analyzer.py"
    "setup.py"
    "README.md"
    "docs/complete_documentation.md"
    "src/utils/adaptive_system.py"
)

missing_files=0
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "✓ ${GREEN}$file existe${NC}"
    else
        echo -e "✗ ${RED}$file no encontrado${NC}"
        ((missing_files++))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo -e "\n${RED}[ERROR] Faltan $missing_files archivos críticos.${NC}"
    exit 1
else
    echo -e "${GREEN}Estructura de proyecto verificada correctamente.${NC}"
fi

# ------------------------------------------------------------
# SECCIÓN 3: Ejecutar pruebas unitarias
# ------------------------------------------------------------
echo -e "\n${YELLOW}[3/7] Ejecutando pruebas unitarias...${NC}"

# Verificar si existe el directorio de pruebas
if [ -d "tests" ]; then
    echo "Ejecutando pruebas unitarias..."
    python -m unittest discover -v tests/ || {
        echo -e "${RED}[ERROR] Las pruebas unitarias fallaron.${NC}"
        exit 1
    }
    echo -e "${GREEN}Pruebas unitarias completadas con éxito.${NC}"
else
    echo -e "${YELLOW}[ADVERTENCIA] No se encontró el directorio de pruebas.${NC}"
fi

# ------------------------------------------------------------
# SECCIÓN 4: Verificación de sistema freemium
# ------------------------------------------------------------
echo -e "\n${YELLOW}[4/7] Verificando sistema freemium...${NC}"

if [ -f "test_freemium_system.py" ]; then
    echo "Ejecutando verificación de sistema freemium..."
    python test_freemium_system.py --setup || {
        echo -e "${RED}[ERROR] La verificación del sistema freemium falló.${NC}"
        exit 1
    }
    echo -e "${GREEN}Sistema freemium verificado correctamente.${NC}"
else
    echo -e "${YELLOW}[ADVERTENCIA] No se encontró el script de verificación de sistema freemium.${NC}"
fi

# ------------------------------------------------------------
# SECCIÓN 5: Verificación de integración con Anthropic
# ------------------------------------------------------------
echo -e "\n${YELLOW}[5/7] Verificando integración con Anthropic...${NC}"

if [ -f "test_anthropic_integration.py" ]; then
    # Verificar si está configurada la clave de API
    if [ -f ".anthropic_api_key" ] || [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "Ejecutando verificación de integración con Anthropic..."
        python test_anthropic_integration.py || {
            echo -e "${YELLOW}[ADVERTENCIA] La verificación de integración con Anthropic falló.${NC}"
            echo -e "${YELLOW}Esto no detendrá el proceso, pero debería revisarse.${NC}"
        }
    else
        echo -e "${YELLOW}[ADVERTENCIA] No se encontró clave de API de Anthropic. Omitiendo pruebas de integración.${NC}"
    fi
else
    echo -e "${YELLOW}[ADVERTENCIA] No se encontró el script de verificación de integración con Anthropic.${NC}"
fi

# ------------------------------------------------------------
# SECCIÓN 6: Generación de paquetes de distribución
# ------------------------------------------------------------
echo -e "\n${YELLOW}[6/7] Generando paquetes de distribución...${NC}"

# Limpiar directorio de distribución si existe
if [ -d "dist" ]; then
    echo "Limpiando directorio de distribución anterior..."
    rm -rf dist/
fi

# Construir paquetes
echo "Generando paquetes de distribución..."
python setup.py sdist bdist_wheel || {
    echo -e "${RED}[ERROR] La generación de paquetes falló.${NC}"
    exit 1
}

echo -e "Verificando paquetes generados..."
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo -e "${GREEN}Paquetes generados correctamente:${NC}"
    ls -la dist/
else
    echo -e "${RED}[ERROR] No se generaron paquetes.${NC}"
    exit 1
fi

# ------------------------------------------------------------
# SECCIÓN 7: Verificación de instalación
# ------------------------------------------------------------
echo -e "\n${YELLOW}[7/7] Verificando instalación del paquete...${NC}"

# Crear entorno virtual para prueba de instalación
echo "Creando entorno virtual para prueba..."
python -m venv test_env || {
    echo -e "${RED}[ERROR] No se pudo crear el entorno virtual.${NC}"
    exit 1
}

# Activar entorno virtual
echo "Activando entorno virtual..."
source test_env/bin/activate || {
    echo -e "${RED}[ERROR] No se pudo activar el entorno virtual.${NC}"
    exit 1
}

# Instalar wheel si no está disponible
pip install wheel

# Instalar el paquete generado
echo "Instalando paquete desde wheel..."
pip install dist/*.whl || {
    echo -e "${RED}[ERROR] La instalación del paquete falló.${NC}"
    deactivate
    exit 1
}

# Verificar importación
echo "Verificando importación del paquete..."
if python -c "import project_prompt; print(f'Versión instalada: {project_prompt.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}Paquete instalado y verificado correctamente.${NC}"
else
    echo -e "${RED}[ERROR] No se pudo importar el paquete instalado.${NC}"
    deactivate
    exit 1
fi

# Desactivar entorno virtual
deactivate

# Limpiar entorno de prueba
echo "Limpiando entorno de prueba..."
rm -rf test_env/

# ------------------------------------------------------------
# RESUMEN FINAL
# ------------------------------------------------------------
echo -e "\n${BLUE}=================================================================="
echo "     ProjectPrompt - Verificación Completada Con Éxito"
echo "==================================================================${NC}"
echo -e "\n${GREEN}Todas las verificaciones pasaron correctamente.${NC}"
echo -e "El proyecto está listo para su publicación.\n"

echo -e "${YELLOW}Pasos finales para publicar:${NC}"
echo -e "1. Revisar la documentación final"
echo -e "2. Actualizar el número de versión en setup.py si es necesario"
echo -e "3. Crear tag en git: git tag -a v1.0.0 -m \"Versión 1.0.0\""
echo -e "4. Subir tag: git push origin v1.0.0"
echo -e "5. Publicar en PyPI: python -m twine upload dist/*\n"

echo -e "Paquetes disponibles en el directorio dist/"
ls -la dist/
