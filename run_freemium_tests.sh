#!/bin/bash
# Script para ejecutar una verificación completa del Sistema de Verificación Freemium

echo -e "\n====================================================="
echo "Verificación completa del Sistema Freemium de ProjectPrompt"
echo "=====================================================\n"

# Obtener directorio actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Verificar opciones
SIMULATE_FLAG=""
if [ "$1" == "--simulate" ]; then
  SIMULATE_FLAG="--simulate-api --simulate-license --simulate-premium"
  echo "Ejecutando en modo simulación..."
fi

# 1. Verificar sistema de licencias
echo -e "\n\033[1m1. Verificando sistema de licencias...\033[0m"
python test_freemium_system.py --test license $SIMULATE_FLAG
if [ $? -ne 0 ]; then
  echo -e "\n\033[31mError en el sistema de licencias. Abortando verificación.\033[0m"
  exit 1
fi

# 2. Verificar sistema de suscripciones
echo -e "\n\033[1m2. Verificando sistema de suscripciones...\033[0m"
python test_freemium_system.py --test subscription $SIMULATE_FLAG
if [ $? -ne 0 ]; then
  echo -e "\n\033[31mError en el sistema de suscripciones. Abortando verificación.\033[0m"
  exit 1
fi

# 3. Verificar integración con Anthropic
echo -e "\n\033[1m3. Verificando integración con Anthropic...\033[0m"
python test_freemium_system.py --test anthropic $SIMULATE_FLAG
if [ $? -ne 0 ]; then
  echo -e "\n\033[33mAdvertencia: La integración con Anthropic no está configurada correctamente.\033[0m"
  echo -e "Para configurar la clave API de Anthropic, use el comando:"
  echo -e "\tpython set_anthropic_key.py --key TU_CLAVE_API"
fi

# 4. Verificar sistema completo
echo -e "\n\033[1m4. Verificando sistema completo...\033[0m"
if [ -n "$SIMULATE_FLAG" ]; then
  python verify_freemium_system.py --simulate
else
  python verify_freemium_system.py
fi

if [ $? -ne 0 ]; then
  echo -e "\n\033[31mError en la verificación del sistema completo.\033[0m"
else
  echo -e "\n\033[32m¡El Sistema de Verificación Freemium está implementado correctamente!\033[0m"
fi

echo -e "\nVerificación finalizada."
exit 0
