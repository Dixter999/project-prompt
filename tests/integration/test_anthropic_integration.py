#!/usr/bin/env python3
"""
Script para probar la integración con la API de Anthropic en ProjectPrompt.
Este script configura la clave API y prueba las funcionalidades premium.
"""

import os
import sys
import getpass
import logging
import argparse
from typing import Dict, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("anthropic_test")

def test_api_validator() -> Tuple[bool, str]:
    """
    Prueba el validador de API para Anthropic.
    
    Returns:
        Tupla con (éxito, mensaje)
    """
    try:
        from src.utils.api_validator import get_api_validator
        
        validator = get_api_validator()
        logger.info("Validador de API cargado correctamente")
        
        # Verificar que Anthropic es una API soportada
        if "anthropic" not in validator.available_apis:
            return False, "La API de Anthropic no está soportada por el validador"
        
        logger.info("La API de Anthropic está soportada")
        return True, "Validador de API configurado correctamente"
    except ImportError as e:
        return False, f"No se pudo importar el validador de API: {e}"
    except Exception as e:
        return False, f"Error al probar el validador de API: {e}"

def test_anthropic_client() -> Tuple[bool, str]:
    """
    Prueba el cliente de la API de Anthropic.
    
    Returns:
        Tupla con (éxito, mensaje)
    """
    try:
        from src.integrations.anthropic import get_anthropic_client, AnthropicAPI
        
        client = get_anthropic_client()
        logger.info("Cliente de Anthropic cargado correctamente")
        
        # Verificar que el cliente está configurado
        if not client.is_configured:
            return False, "El cliente de Anthropic no está configurado (falta clave API)"
        
        # Validar la clave API
        success, message = client.verify_api_key()
        if not success:
            return False, f"La clave API de Anthropic no es válida: {message}"
        
        logger.info("Cliente de Anthropic configurado y clave API válida")
        return True, "Cliente de Anthropic configurado correctamente"
    except ImportError as e:
        return False, f"No se pudo importar el cliente de Anthropic: {e}"
    except Exception as e:
        return False, f"Error al probar el cliente de Anthropic: {e}"

def test_premium_access() -> Tuple[bool, str]:
    """
    Prueba el acceso premium a través de la API de Anthropic.
    
    Returns:
        Tupla con (éxito, mensaje)
    """
    try:
        from src.integrations.anthropic_advanced import get_advanced_anthropic_client
        from src.utils.subscription_manager import get_subscription_manager
        
        # Verificar que el gestor de suscripciones está disponible
        subscription = get_subscription_manager()
        if subscription._subscription_type == "free":
            logger.warning("Usuario con suscripción gratuita, las pruebas premium pueden fallar")
        
        # Verificar cliente avanzado
        client = get_advanced_anthropic_client()
        if not client.is_configured:
            return False, "El cliente avanzado de Anthropic no está configurado"
        
        # Verificar acceso premium
        has_access = client.verify_premium_access()
        if not has_access:
            return False, "No se tiene acceso premium a las funcionalidades de Anthropic"
        
        logger.info("Acceso premium a Anthropic verificado correctamente")
        return True, "Acceso premium a Anthropic configurado correctamente"
    except ImportError as e:
        return False, f"No se pudo importar el cliente avanzado de Anthropic: {e}"
    except Exception as e:
        return False, f"Error al probar el acceso premium a Anthropic: {e}"

def set_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Configura la clave API de Anthropic.
    
    Args:
        api_key: Clave API de Anthropic
    
    Returns:
        Tupla con (éxito, mensaje)
    """
    try:
        # Intentar usar el script de configuración directo
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_anthropic_key.py")
        if os.path.exists(script_path):
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from set_anthropic_key import validate_api_key
            
            success, message = validate_api_key(api_key)
            return success, message
        
        # Alternativa: usar el validador de API directamente
        from src.utils.api_validator import get_api_validator
        
        validator = get_api_validator()
        success, message = validator.set_api_key("anthropic", api_key)
        
        if success:
            # Validar la clave después de guardarla
            result = validator.validate_api("anthropic")
            if result.get("valid", False):
                return True, "Clave API de Anthropic configurada y validada correctamente"
            else:
                return False, f"La clave se guardó pero no pasó la validación: {result.get('message')}"
        else:
            return False, f"Error al guardar la clave API: {message}"
    except Exception as e:
        return False, f"Error al configurar la clave API: {e}"

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Configurar la clave API de Anthropic para ProjectPrompt')
    parser.add_argument('api_key', nargs='?', help='Clave API de Anthropic')
    parser.add_argument('--validate-only', action='store_true', help='Solo validar la clave sin guardarla')
    args = parser.parse_args()
    
    # Try to get API key from .env file first
    api_key = None
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API")
        if api_key:
            logger.info("Clave API encontrada en archivo .env")
    except ImportError:
        logger.debug("python-dotenv no está instalado, no se puede cargar de .env")
    
    # If not provided in .env, use command line argument
    if not api_key and args.api_key:
        api_key = args.api_key
    
    # If still not available, prompt user
    if not api_key:
        try:
            import getpass
            api_key = getpass.getpass("Introduce tu clave API de Anthropic: ")
        except Exception as e:
            logger.error(f"Error al leer la entrada: {e}")
            return 1
    
    success, message = set_api_key(api_key)
    
    if success:
        logger.info(f"✅ {message}")
        return 0
    else:
        logger.error(f"❌ {message}")
        return 1
    
    # Probar la integración
    if args.test:
        tests = [
            ("Validador de API", test_api_validator),
            ("Cliente de Anthropic", test_anthropic_client),
            ("Acceso Premium", test_premium_access)
        ]
        
        success_count = 0
        for name, test_func in tests:
            logger.info(f"Ejecutando prueba: {name}")
            success, message = test_func()
            
            if success:
                logger.info(f"✅ {name}: {message}")
                success_count += 1
            else:
                logger.error(f"❌ {name}: {message}")
        
        # Imprimir resumen
        print("\n" + "=" * 50)
        print(f"RESUMEN: {success_count}/{len(tests)} pruebas exitosas")
        print("=" * 50)
        
        return 0 if success_count == len(tests) else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
