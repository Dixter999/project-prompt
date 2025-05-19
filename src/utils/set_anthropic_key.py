#!/usr/bin/env python3
"""
Script para configurar la clave API de Anthropic para ProjectPrompt.
Este script integra con el Sistema de Verificación Freemium para validar y configurar
el acceso a la API de Anthropic según el tipo de suscripción del usuario.
"""

import os
import sys
import yaml
import logging
import argparse
from typing import Optional, Dict, Any, Tuple

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constantes
CONFIG_DIR = os.path.expanduser("~/.config/project-prompt")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
SERVICE_NAME = "project-prompt"
API_VALIDATOR_PATH = None  # Se llenará dinámicamente

def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Valida la clave API de Anthropic contra su servicio.
    
    Args:
        api_key: Clave API de Anthropic a validar
        
    Returns:
        Tupla con (éxito, mensaje)
    """
    try:
        # Primero intentamos importar del proyecto
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.utils.api_validator import get_api_validator
            
            # Usar el validador de APIs integrado
            validator = get_api_validator()
            success, message = validator.set_api_key("anthropic", api_key)
            
            if success:
                # Validar la clave con Anthropic
                result = validator.validate_api("anthropic")
                if result.get("valid", False):
                    return True, "La clave API de Anthropic ha sido verificada exitosamente."
                else:
                    return False, f"La clave se guardó pero no pasó la verificación: {result.get('message')}"
            else:
                return False, f"Error al guardar la clave: {message}"
                
        except ImportError:
            # Si no se puede importar, usamos la implementación standalone
            logger.info("No se pudo importar el validador integrado. Usando validación básica...")
            return set_anthropic_api_key_standalone(api_key)
            
    except Exception as e:
        logger.error(f"Error al validar la clave API: {e}")
        return False, f"Error durante la validación: {e}"

def set_anthropic_api_key_standalone(api_key: str) -> Tuple[bool, str]:
    """
    Configura la clave API de Anthropic utilizando el mecanismo standalone.
    
    Args:
        api_key: Clave API de Anthropic
        
    Returns:
        Tupla con (éxito, mensaje)
    """
    # Crear directorio de configuración si no existe
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Cargar configuración existente o crear una nueva
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Configuración existente cargada desde {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error al leer la configuración: {e}")
            logger.info("Creando nueva configuración desde cero")
    
    # Añadir o actualizar la clave API de Anthropic
    if 'api' not in config:
        config['api'] = {}
    if 'anthropic' not in config['api']:
        config['api']['anthropic'] = {}
    
    config['api']['anthropic']['key'] = api_key
    config['api']['anthropic']['enabled'] = True
    
    # Guardar la configuración
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.info(f"Clave API de Anthropic guardada correctamente en {CONFIG_FILE}")
        return True, f"Clave API guardada correctamente en {CONFIG_FILE}"
    except Exception as e:
        logger.error(f"Error al guardar la configuración: {e}")
        return False, f"Error al guardar la configuración: {e}"

def read_api_key_from_env():
    """
    Lee la clave API de Anthropic desde el archivo .env.
    
    Returns:
        str: La clave API o None si no se encuentra
    """
    try:
        # Intentar leer directamente del archivo .env
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('anthropic_API'):
                        parts = line.split('=', 1)
                        if len(parts) >= 2:
                            return parts[1].strip().strip('"\'')
        
        # Si no se encuentra en el archivo, intentar con dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("anthropic_API")
            if api_key:
                return api_key
        except ImportError:
            logger.debug("python-dotenv no está instalado, no se puede cargar de .env con biblioteca")
        
        return None
    except Exception as e:
        logger.error(f"Error al leer el archivo .env: {e}")
        return None

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Configurar la clave API de Anthropic para ProjectPrompt')
    parser.add_argument('api_key', nargs='?', help='Clave API de Anthropic (opcional, se usa .env por defecto)')
    parser.add_argument('--validate-only', action='store_true', help='Solo validar la clave sin guardarla')
    args = parser.parse_args()
    
    # Obtener la clave API desde .env
    api_key = read_api_key_from_env()
    if api_key:
        logger.info("Clave API encontrada en archivo .env")
    
    # Si no está en .env, usar argumento de línea de comandos
    if not api_key and args.api_key:
        api_key = args.api_key
        
    # Si aún no hay clave API, mostrar error
    if not api_key:
        logger.error("No se encontró la clave API de Anthropic en el archivo .env")
        logger.error("Asegúrate de tener un archivo .env con la variable anthropic_API definida")
        return 1
    
    success, message = validate_api_key(api_key)
    
    if success:
        logger.info(f"✅ {message}")
        return 0
    else:
        logger.error(f"❌ {message}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
