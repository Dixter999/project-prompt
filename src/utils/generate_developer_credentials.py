#!/usr/bin/env python3
"""
Script para generar credenciales de desarrollador para ProjectPrompt.
Este script genera claves de licencia de desarrollador y configura las credenciales
necesarias para acceder a las funciones premium de ProjectPrompt.

En una implementación futura, estas credenciales se almacenarán en una base de datos
relacionada con el email y la contraseña del usuario registrado.
"""

import os
import sys
import time
import hmac
import json
import hashlib
import argparse
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any, Union

# Configurar la importación de módulos del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Variables globales
CONFIG_DIR = os.path.expanduser("~/.config/project-prompt")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "developer_credentials.json")

# Clave secreta para verificación (debe coincidir con la de license_validator.py)
_VERIFICATION_SECRET = "projectprompt_dev_license_validation_2023"

# Tipos de suscripción disponibles
SUBSCRIPTION_TYPES = ["basic", "pro", "team"]


def setup_argument_parser():
    """Configurar el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Generador de credenciales de desarrollador para ProjectPrompt"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        help="Nombre del desarrollador"
    )
    
    parser.add_argument(
        "--email",
        type=str,
        help="Correo electrónico del desarrollador"
    )
    
    parser.add_argument(
        "--type",
        type=str,
        choices=SUBSCRIPTION_TYPES,
        default="pro",
        help="Tipo de suscripción (basic, pro, team)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Días de validez de la licencia"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar regeneración de credenciales si ya existen"
    )
    
    parser.add_argument(
        "--anthropic-key",
        type=str,
        help="Clave API de Anthropic (opcional)"
    )
    
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Solo verificar las credenciales existentes sin generar nuevas"
    )
    
    return parser


def generate_license_hash(data: str) -> str:
    """
    Genera un hash para verificar la integridad de la licencia.
    
    Args:
        data: Datos a hashear
        
    Returns:
        Hash hexadecimal truncado
    """
    key = _VERIFICATION_SECRET.encode('utf-8')
    data_bytes = data.encode('utf-8')
    hmac_sha256 = hmac.new(key, data_bytes, hashlib.sha256)
    digest = hmac_sha256.hexdigest()
    return digest[:15]  # Truncar a 15 caracteres


def generate_license_key(subscription_type: str, days_valid: int) -> str:
    """
    Genera una clave de licencia válida.
    
    Args:
        subscription_type: Tipo de suscripción (basic, pro, team)
        days_valid: Número de días de validez de la licencia
        
    Returns:
        Clave de licencia generada
    """
    # Calcular fecha de expiración
    expiration_date = datetime.now() + timedelta(days=days_valid)
    expiration_str = expiration_date.strftime("%Y%m%d")
    
    # Crear la parte base de la licencia
    subscription_type = subscription_type.upper()
    base_license = f"PP-{subscription_type}-{expiration_str}"
    
    # Generar hash de verificación
    verification_hash = generate_license_hash(base_license)
    
    # Crear la licencia completa
    license_key = f"{base_license}-{verification_hash}"
    
    return license_key


def save_developer_credentials(credentials: Dict[str, Any]) -> bool:
    """
    Guarda las credenciales de desarrollador en el archivo de configuración.
    
    Args:
        credentials: Diccionario con las credenciales
        
    Returns:
        True si se guardaron correctamente, False en caso contrario
    """
    try:
        # Asegurarse de que el directorio de configuración existe
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Guardar las credenciales en formato JSON
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"✅ Credenciales guardadas en: {CREDENTIALS_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar las credenciales: {e}")
        return False


def configure_license_key(license_key: str) -> bool:
    """
    Configura la clave de licencia en el sistema.
    
    Args:
        license_key: Clave de licencia a configurar
        
    Returns:
        True si se configuró correctamente, False en caso contrario
    """
    try:
        # Importar el módulo de gestión de suscripciones
        try:
            from src.utils.subscription_manager import SubscriptionManager
            
            # Usar el gestor de suscripciones integrado
            manager = SubscriptionManager()
            result = manager.activate_license(license_key)
            
            if result:
                print(f"✅ Licencia activada correctamente: {license_key}")
                return True
            else:
                print(f"❌ No se pudo activar la licencia a través del SubscriptionManager")
                # Fallback a la configuración manual
                
        except ImportError:
            print("⚠️ No se pudo importar el gestor de suscripciones. Configurando manualmente...")
            
        # Configuración manual en archivo de configuración
        import yaml
        
        # Crear el archivo de configuración si no existe
        if not os.path.exists(CONFIG_FILE):
            config = {}
        else:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
        
        # Asegurarse de que la sección 'subscription' existe
        if 'subscription' not in config:
            config['subscription'] = {}
            
        # Configurar la licencia
        config['subscription']['license_key'] = license_key
        
        # Guardar la configuración
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        print(f"✅ Licencia configurada manualmente en: {CONFIG_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Error al configurar la licencia: {e}")
        return False


def verify_existing_credentials():
    """Verificar las credenciales existentes."""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ No existen credenciales en {CREDENTIALS_FILE}")
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
            
        print("\n=== Credenciales de Desarrollador ===")
        print(f"  Nombre: {credentials.get('name', 'N/A')}")
        print(f"  Email: {credentials.get('email', 'N/A')}")
        print(f"  Tipo: {credentials.get('subscription_type', 'N/A')}")
        print(f"  Licencia: {credentials.get('license_key', 'N/A')}")
        print(f"  Expira: {credentials.get('expiration_date', 'N/A')}")
        
        # Verificar si la licencia está configurada en config.yaml
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = yaml.safe_load(f) or {}
                
                license_in_config = config.get('subscription', {}).get('license_key')
                if license_in_config == credentials.get('license_key'):
                    print("\n✅ La licencia está correctamente configurada en config.yaml")
                else:
                    print("\n❌ La licencia en config.yaml no coincide con las credenciales")
                    print(f"  En config.yaml: {license_in_config}")
                    print(f"  En credenciales: {credentials.get('license_key')}")
            except Exception as e:
                print(f"\n❌ Error al leer config.yaml: {e}")
        else:
            print("\n❌ No existe el archivo config.yaml")
        
        # Verificar la API key de Anthropic si está configurada
        anthropic_key = config.get('apis', {}).get('anthropic', {}).get('api_key')
        if anthropic_key:
            print("\n✅ API key de Anthropic configurada")
        else:
            print("\n❌ No hay API key de Anthropic configurada")
        
        return True
    except Exception as e:
        print(f"❌ Error al leer credenciales: {e}")
        return False

def configure_anthropic_key(api_key: str) -> bool:
    """
    Configura la clave API de Anthropic.
    
    Args:
        api_key: Clave API a configurar
        
    Returns:
        True si se configuró correctamente, False en caso contrario
    """
    try:
        # Primero intentamos usar el módulo de validación de APIs
        try:
            from src.utils.api_validator import get_api_validator
            
            validator = get_api_validator()
            success, message = validator.set_api_key("anthropic", api_key)
            
            if success:
                print(f"✅ API key de Anthropic configurada correctamente mediante API validator")
                return True
            else:
                print(f"❌ No se pudo configurar la API key: {message}")
                # Continuar con la configuración manual
        except ImportError:
            print("ℹ️ No se pudo importar el validador de APIs, configurando manualmente...")
        
        # Configuración manual en config.yaml
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Asegurarse de que las secciones necesarias existen
        if 'apis' not in config:
            config['apis'] = {}
        if 'anthropic' not in config['apis']:
            config['apis']['anthropic'] = {}
        
        # Establecer la API key
        config['apis']['anthropic']['api_key'] = api_key
        
        # Guardar la configuración
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ API key de Anthropic guardada en {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error al configurar API key: {e}")
        return False

def main():
    """Función principal del script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Verificar credenciales existentes
    if args.verify_only:
        verify_existing_credentials()
        return
    
    # Verificar si ya existen credenciales
    if os.path.exists(CREDENTIALS_FILE) and not args.force:
        print(f"⚠️ Ya existen credenciales en {CREDENTIALS_FILE}")
        print("Use --force para regenerarlas")
        verify_existing_credentials()
        return
    
    # Solicitar información al usuario si no se proporcionó
    name = args.name
    if not name:
        name = input("Nombre del desarrollador: ")
    
    email = args.email
    if not email:
        email = input("Correo electrónico: ")
    
    subscription_type = args.type.lower()
    days_valid = args.days
    
    print("\nGenerando credenciales de desarrollador...")
    print(f"  Nombre: {name}")
    print(f"  Email: {email}")
    print(f"  Tipo de suscripción: {subscription_type}")
    print(f"  Validez: {days_valid} días")
    
    # Generar clave de licencia
    license_key = generate_license_key(subscription_type, days_valid)
    
    # Crear el objeto de credenciales
    expiration_date = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    credentials = {
        "name": name,
        "email": email,
        "subscription_type": subscription_type,
        "license_key": license_key,
        "expiration_date": expiration_date,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_developer": True
    }
    
    # Guardar las credenciales
    if save_developer_credentials(credentials):
        print("\n🔑 Credenciales generadas exitosamente:")
        print(f"  Licencia: {license_key}")
        print(f"  Expira el: {expiration_date}")
        
        # Configurar la licencia en el sistema
        license_configured = configure_license_key(license_key)
        
        # Si se proporcionó una API key de Anthropic, configurarla
        anthropic_key_configured = False
        if args.anthropic_key:
            anthropic_key_configured = configure_anthropic_key(args.anthropic_key)
        
        if license_configured:
            print("\n✨ Modelo premium activado correctamente!")
            print("Ahora puedes usar todas las funcionalidades premium de ProjectPrompt.")
            
            if not anthropic_key_configured and args.anthropic_key:
                print("\n⚠️ No se pudo configurar la API key de Anthropic.")
            elif args.anthropic_key:
                print("\n✅ API key de Anthropic configurada correctamente.")
            else:
                print("\nℹ️ No se proporcionó API key de Anthropic. Algunas funciones premium pueden no estar disponibles.")
                print("   Para añadir una API key más tarde, usa:")
                print("   python generate_developer_credentials.py --verify-only --anthropic-key=TU_API_KEY")
            
            # Mostrar comandos disponibles
            print("\n📋 Comandos disponibles:")
            print("  python verify_freemium_system.py           # Verificar estado del sistema freemium")
            print("  python verify_dev_credentials.py           # Verificar credenciales de desarrollador")
            try:
                from src.generators.contextual_prompt_generator import ContextualPromptGenerator
                print("  python examples/demo_enhanced_prompts.py  # Para probar funciones avanzadas")
            except ImportError:
                print("  python examples/simple_premium_demo.py    # Para probar funciones básicas premium")
        else:
            print("\n⚠️ No se pudo activar automáticamente el modelo premium.")
            print(f"Para activarlo manualmente, ejecute: python verify_freemium_system.py")


if __name__ == "__main__":
    main()
