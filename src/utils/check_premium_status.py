#!/usr/bin/env python3
"""
Script para verificar el estado actual de la licencia premium.
"""

import os
import sys
import yaml
from pathlib import Path
import argparse

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent))

def get_subscription_info():
    """Obtener información de la suscripción actual."""
    
    # Inicializar resultados
    results = {
        "license_key": None,
        "subscription_type": "free",
        "is_valid": False,
        "expiration_date": None,
        "status_message": "No se encontró información de licencia."
    }
    
    # Verificar archivo de credenciales de desarrollador
    dev_credentials_path = os.path.expanduser("~/.config/project-prompt/developer_credentials.json")
    if os.path.exists(dev_credentials_path):
        import json
        try:
            with open(dev_credentials_path, 'r') as f:
                credentials = json.load(f)
                
            results["license_key"] = credentials.get("license_key")
            results["subscription_type"] = credentials.get("subscription_type", "free")
            results["is_valid"] = True
            results["expiration_date"] = credentials.get("expiration_date")
            results["status_message"] = "Credenciales de desarrollador encontradas y válidas."
            results["is_developer"] = True
            results["developer_name"] = credentials.get("name")
            results["developer_email"] = credentials.get("email")
            
            return results
            
        except Exception as e:
            print(f"Error al leer credenciales de desarrollador: {e}")
    
    # Verificar archivo de configuración
    config_path = os.path.expanduser("~/.config/project-prompt/config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
                
            license_key = config.get("subscription", {}).get("license_key")
            if license_key:
                results["license_key"] = license_key
                
                # Intentar validar con el validador de licencias
                try:
                    from src.utils.license_validator import get_license_validator
                    validator = get_license_validator()
                    status = validator.validate_license(license_key)
                    
                    results["is_valid"] = status.valid
                    results["subscription_type"] = status.subscription_type
                    results["expiration_date"] = status.expiration_date
                    
                    if status.valid:
                        results["status_message"] = f"Licencia válida: {status.subscription_type}"
                        
                        if status.expired:
                            results["status_message"] += " (EXPIRADA)"
                            results["is_valid"] = False
                    else:
                        results["status_message"] = "La licencia no es válida."
                        
                except ImportError:
                    results["status_message"] = "Licencia encontrada pero no se pudo validar (módulo no disponible)."
            else:
                results["status_message"] = "No se encontró clave de licencia en la configuración."
                
            return results
            
        except Exception as e:
            print(f"Error al leer configuración: {e}")
    
    return results

def check_premium_capabilities():
    """Verificar si las capacidades premium están disponibles."""
    capabilities = {
        "enhanced_prompts": False,
        "anthropic_api": False,
        "openai_api": False
    }
    
    # Verificar disponibilidad del generador de prompts contextual
    try:
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        capabilities["enhanced_prompts"] = True
    except ImportError:
        pass
    
    # Verificar configuración de Anthropic API
    try:
        from src.utils.api_validator import get_api_validator
        validator = get_api_validator()
        anthropic_status = validator.validate_api("anthropic")
        capabilities["anthropic_api"] = anthropic_status.get("valid", False)
    except ImportError:
        pass
    
    # Verificar configuración de OpenAI API
    try:
        from src.utils.api_validator import get_api_validator
        validator = get_api_validator()
        openai_status = validator.validate_api("openai")
        capabilities["openai_api"] = openai_status.get("valid", False)
    except ImportError:
        pass
    
    return capabilities

def format_table_row(label, value):
    """Formatear una fila de tabla para la salida."""
    return f"| {label.ljust(20)} | {str(value).ljust(40)} |"

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Verificador de estado premium de ProjectPrompt")
    parser.add_argument("--json", action="store_true", help="Mostrar resultados en formato JSON")
    args = parser.parse_args()
    
    # Obtener información de suscripción
    subscription_info = get_subscription_info()
    capabilities = check_premium_capabilities()
    
    # Determinar estado general
    is_premium = subscription_info["is_valid"] and subscription_info["subscription_type"] in ["basic", "pro", "team"]
    
    if args.json:
        import json
        result = {
            "subscription": subscription_info,
            "capabilities": capabilities,
            "is_premium_active": is_premium
        }
        print(json.dumps(result, indent=2))
        return
    
    # Mostrar resultados en formato legible
    print("═══════════════════════════════════════════════════════════════════════════")
    print("           VERIFICACIÓN DE ESTADO PREMIUM DE PROJECTPROMPT                ")
    print("═══════════════════════════════════════════════════════════════════════════")
    
    # Información de licencia
    print("\n--- INFORMACIÓN DE LICENCIA ---")
    print("┌──────────────────────┬─────────────────────────────────────────┐")
    print(format_table_row("Estado Premium", "ACTIVO ✅" if is_premium else "INACTIVO ❌"))
    print(format_table_row("Clave de Licencia", subscription_info["license_key"] or "No configurada"))
    print(format_table_row("Tipo de Suscripción", subscription_info["subscription_type"]))
    print(format_table_row("Válida", "Sí ✓" if subscription_info["is_valid"] else "No ✗"))
    print(format_table_row("Fecha de Expiración", subscription_info["expiration_date"] or "N/A"))
    print(format_table_row("Mensaje de Estado", subscription_info["status_message"]))
    
    # Información adicional para desarrolladores
    if subscription_info.get("is_developer"):
        print("├──────────────────────┴─────────────────────────────────────────┤")
        print("│                  CREDENCIALES DE DESARROLLADOR                 │")
        print("├──────────────────────┬─────────────────────────────────────────┤")
        print(format_table_row("Nombre", subscription_info.get("developer_name", "N/A")))
        print(format_table_row("Email", subscription_info.get("developer_email", "N/A")))
    
    print("└──────────────────────┴─────────────────────────────────────────┘")
    
    # Capacidades premium
    print("\n--- CAPACIDADES PREMIUM ---")
    print("┌──────────────────────┬─────────────────────────────────────────┐")
    print(format_table_row("Prompts Mejorados", "Disponible ✓" if capabilities["enhanced_prompts"] else "No disponible ✗"))
    print(format_table_row("API Anthropic", "Configurada ✓" if capabilities["anthropic_api"] else "No configurada ✗"))
    print(format_table_row("API OpenAI", "Configurada ✓" if capabilities["openai_api"] else "No configurada ✗"))
    print("└──────────────────────┴─────────────────────────────────────────┘")
    
    # Instrucciones adicionales
    print("\n--- INSTRUCCIONES ---")
    if is_premium:
        print("✅ Las funciones premium están activadas correctamente.")
        print("   Puedes utilizar todas las capacidades avanzadas del sistema.")
        print("\nPara probar las funcionalidades premium:")
        print("  python examples/simple_premium_demo.py")
    else:
        print("❌ Las funciones premium no están activadas.")
        print("   Para activar el modo premium ejecuta:")
        print("   python generate_developer_credentials.py")
        
        if subscription_info["license_key"]:
            print("\n⚠️ Hay una licencia configurada pero no es válida o ha expirado.")
            print("   Considera generar una nueva licencia de desarrollador.")
    
    print("\n═══════════════════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    main()
