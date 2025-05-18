#!/usr/bin/env bash
# setup_environment.sh
#
# Script de configuración del entorno para ProjectPrompt
# Este script automatiza la configuración del entorno para ProjectPrompt
# en sistemas Linux y macOS.

set -e  # Salir en caso de error

# Colores para mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin Color

echo -e "${BLUE}=== Configuración de Entorno para ProjectPrompt ===${NC}"
echo -e "${BLUE}=================================================${NC}\n"

# Verificar Python
echo -e "${YELLOW}Verificando instalación de Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python instalado: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 3 no está instalado.${NC}"
    echo -e "${YELLOW}Por favor instala Python 3.8 o superior antes de continuar.${NC}"
    exit 1
fi

# Verificar pip
echo -e "${YELLOW}Verificando instalación de pip...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓ pip instalado: ${PIP_VERSION}${NC}"
else
    echo -e "${RED}✗ pip no está instalado.${NC}"
    echo -e "${YELLOW}Instalando pip...${NC}"
    python3 -m ensurepip --upgrade
fi

# Crear entorno virtual
echo -e "\n${YELLOW}Creando entorno virtual...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# Activar entorno virtual
echo -e "${YELLOW}Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"

# Actualizar pip
echo -e "\n${YELLOW}Actualizando pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✓ pip actualizado a la última versión${NC}"

# Instalar dependencias
echo -e "\n${YELLOW}Instalando dependencias...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"

# Configurar acceso directo
echo -e "\n${YELLOW}Configurando acceso directo...${NC}"
mkdir -p $HOME/bin
ln -sf $(pwd)/project_prompt.py $HOME/bin/project-prompt
chmod +x $HOME/bin/project-prompt
chmod +x *.sh

# Verificar variable PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo -e "${YELLOW}Añadiendo $HOME/bin a PATH...${NC}"
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> $HOME/.zshrc
        echo -e "${GREEN}✓ PATH actualizado en .zshrc${NC}"
    elif [ -f "$HOME/.bashrc" ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> $HOME/.bashrc
        echo -e "${GREEN}✓ PATH actualizado en .bashrc${NC}"
    else
        echo -e "${RED}✗ No se pudo encontrar .zshrc o .bashrc. Por favor añade $HOME/bin a tu PATH manualmente${NC}"
    fi
else
    echo -e "${GREEN}✓ $HOME/bin ya está en PATH${NC}"
fi

# Mensaje final
echo -e "\n${GREEN}=== Configuración completada ===${NC}"
echo -e "${YELLOW}Para utilizar ProjectPrompt, prueba alguno de estos comandos:${NC}"
echo -e "${BLUE}project-prompt --help${NC}"
echo -e "${BLUE}project-prompt analyze .${NC}"
echo -e "${BLUE}project-prompt init mi-proyecto${NC}\n"

echo -e "${YELLOW}Para activar el entorno virtual en nuevas sesiones:${NC}"
echo -e "${BLUE}cd $(pwd) && source venv/bin/activate${NC}\n"

echo -e "${GREEN}¡Gracias por usar ProjectPrompt!${NC}"
