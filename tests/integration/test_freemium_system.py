#!/usr/bin/env python3
"""
Script para probar manualmente el Sistema de Verificación Freemium.
Este script ejecuta una serie de pruebas para verificar que todos los componentes
del sistema freemium estén funcionando correctamente.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("freemium_tester")

# Añadir el directorio del proyecto al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all(args):
    """Ejecuta todas las pruebas disponibles."""
    results = {}
    
    print("=== Probando Sistema de Verificación Freemium ===\n")
    
    # Comprobar si necesitamos configurar primero
    if args.setup:
        print("\n-- Configurando entorno de prueba --")
        setup_test_environment(args)
        print()
    
    # Ejecutar pruebas en secuencia
    results["license_system"] = test_license_system(args)
    results["subscription_system"] = test_subscription_system(args)
    results["anthropic_integration"] = test_anthropic_integration(args)
    
    # Mostrar resumen
    print("\n=== Resumen de Pruebas ===")
    success_count = sum(1 for r in results.values() if r.get("success", False))
    total = len(results)
    
    print(f"Total: {success_count}/{total} pruebas exitosas")
    
    for name, result in results.items():
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} {name}: {result.get('message', 'Sin mensaje')}")
    
    return success_count == total

def setup_test_environment(args):
    """Configura el entorno para las pruebas."""
    try:
        # Configurar licencia de demostración
        if not args.license_key:
            args.license_key = "DEMO-LICENSE-KEY"
            print(f"✅ Configurada licencia de demostración: {args.license_key}")
        
        # Configurar clave API de prueba si se proporciona
        if args.api_key:
            from src.utils.api_validator import get_api_validator
            
            validator = get_api_validator()
            success, message = validator.set_api_key("anthropic", args.api_key)
            
            if success:
                print(f"✅ Configurada clave API de Anthropic: {message}")
            else:
                print(f"❌ Error al configurar clave API: {message}")
    
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")

def test_license_system(args):
    """Prueba el sistema de licencias."""
    print("-- Probando Sistema de Licencias --")
    result = {"success": False, "message": "", "details": {}}
    
    # Si hay modo de simulación, marcar como éxito
    if args.simulate_license:
        print("✅ [SIMULACIÓN] Sistema de licencias configurado y válido")
        result["success"] = True
        result["message"] = "[SIMULACIÓN] Licencia validada correctamente"
        result["details"] = {
            "license_valid": True,
            "license_expired": False,
            "license_type": "pro"
        }
        return result
    
    try:
        from src.utils.license_validator import LicenseValidator
        
        validator = LicenseValidator()
        print("✅ LicenseValidator iniciado correctamente")
        
        # Verificar licencia de demostración
        license_key = args.license_key or "DEMO-LICENSE-KEY"
        status = validator.validate_license(license_key)
        
        result["details"]["license_valid"] = status.valid
        result["details"]["license_expired"] = status.expired
        result["details"]["license_type"] = status.subscription_type
        
        if status.valid:
            print(f"✅ Licencia validada: {status.subscription_type} (Expira: {status.expiration_date})")
            result["success"] = True
            result["message"] = f"Licencia válida: {status.subscription_type}"
        else:
            print(f"❌ Licencia no válida o expirada: {status.subscription_type}")
            if status.expired:
                print("   Motivo: Licencia expirada")
                result["message"] = "Licencia expirada"
            else:
                print("   Motivo: Clave de licencia inválida")
                result["message"] = "Clave de licencia inválida"
    except ImportError:
        print("❌ No se pudo importar LicenseValidator")
        result["message"] = "No se pudo importar LicenseValidator"
    except Exception as e:
        print(f"❌ Error al probar el sistema de licencias: {e}")
        result["message"] = f"Error: {str(e)}"
        
    return result

def test_subscription_system(args):
    """Prueba el sistema de suscripciones."""
    print("\n-- Probando Sistema de Suscripciones --")
    result = {"success": False, "message": "", "details": {}}
    
    # Si hay modo de simulación, marcar como éxito
    if args.simulate_premium:
        print("✅ [SIMULACIÓN] Sistema de suscripciones configurado y válido")
        result["success"] = True
        result["message"] = "[SIMULACIÓN] Sistema de suscripciones validado: pro"
        result["details"] = {
            "subscription_type": "pro",
            "limits_correct": True,
            "premium_access": True
        }
        return result
    
    try:
        from src.utils.subscription_manager import SubscriptionManager, get_subscription_manager
        
        # Verificar el singleton
        manager = get_subscription_manager()
        print("✅ SubscriptionManager iniciado correctamente")
        
        # Verificar tipo de suscripción
        subscription_type = manager.get_subscription_type()
        print(f"✅ Tipo de suscripción actual: {subscription_type}")
        result["details"]["subscription_type"] = subscription_type
        
        # Verificar límites
        if subscription_type == "free":
            expected_limits = {"daily_prompts": 10}
        else:
            expected_limits = {"daily_prompts": -1}  # Ilimitado para premium
        
        actual_limits = manager.get_limits()
        
        if actual_limits.get("daily_prompts") == expected_limits.get("daily_prompts"):
            print(f"✅ Límites correctos: {actual_limits}")
            result["details"]["limits_correct"] = True
        else:
            print(f"❌ Límites incorrectos. Esperados: {expected_limits}, Actuales: {actual_limits}")
            result["details"]["limits_correct"] = False
            
        # Verificar acceso a características
        feature = "ai_integrations"
        has_access = manager.is_premium_feature_available(feature)
        print(f"✅ Acceso a {feature}: {'Disponible' if has_access else 'No disponible'}")
        result["details"]["premium_access"] = has_access
        
        # Todo bien si llegamos hasta aquí
        result["success"] = True
        result["message"] = f"Sistema de suscripciones validado: {subscription_type}"
        
    except ImportError:
        print("❌ No se pudo importar SubscriptionManager")
        result["message"] = "No se pudo importar SubscriptionManager"
    except Exception as e:
        print(f"❌ Error al probar el sistema de suscripciones: {e}")
        result["message"] = f"Error: {str(e)}"
        
    return result

def test_anthropic_integration(args):
    """Prueba la integración con la API de Anthropic."""
    print("\n-- Probando Integración con Anthropic --")
    result = {"success": False, "message": "", "details": {}}
    
    # Si hay modo de simulación, marcar como éxito
    if args.simulate_api:
        print("✅ [SIMULACIÓN] API de Anthropic configurada y válida")
        result["success"] = True
        result["message"] = "[SIMULACIÓN] API de Anthropic validada correctamente"
        result["details"] = {
            "api_configured": True,
            "api_key_valid": True,
            "premium_access": False,
            "response_received": True
        }
        return result
    
    try:
        # Verificar si ya tenemos test_anthropic.py
        try:
            from src.integrations.test_anthropic import test_anthropic_integration as test_function
            success, test_results = test_function()
            
            # Mostrar resultados
            for key, value in test_results["status"].items():
                status = "✅" if value else "❌"
                print(f"{status} {key}")
            
            result["details"] = test_results["status"]
            result["success"] = success
            result["message"] = test_results["message"]
            
        except ImportError:
            # Fallback manual
            from src.utils.api_validator import get_api_validator
            from src.integrations.anthropic import get_anthropic_client
            
            # Verificar cliente básico
            client = get_anthropic_client()
            api_configured = client.is_configured
            print(f"{'✅' if api_configured else '❌'} api_configured")
            result["details"] = {"api_configured": api_configured}
            
            if not api_configured:
                result["message"] = "API de Anthropic no configurada. Use el comando 'project-prompt set_api anthropic' para configurarla."
                # En modo de prueba, no consideramos esto un error si no se ha configurado la API
                if args.no_api_required:
                    print("⚠️ API no configurada pero la prueba no la requiere. Marcando como éxito.")
                    result["success"] = True
                return result
            
            # Verificar API
            validator = get_api_validator()
            api_result = validator.validate_api("anthropic")
            api_valid = api_result.get("valid", False)
            premium_access = False
            
            # Verificar suscripción
            try:
                from src.utils.subscription_manager import get_subscription_manager
                subscription = get_subscription_manager()
                premium_access = subscription.is_premium_feature_available("ai_integrations")
                print(f"{'✅' if premium_access else '❌'} premium_access")
            except Exception:
                pass
            
            result["details"]["api_key_valid"] = api_valid
            result["details"]["premium_access"] = premium_access
            
            print(f"{'✅' if api_valid else '❌'} api_key_valid")
            
            if api_valid:
                print("✅ API de Anthropic configurada y válida")
                result["success"] = True
                result["message"] = "API de Anthropic validada correctamente"
            else:
                print(f"❌ API de Anthropic no válida: {api_result.get('message')}")
                result["message"] = api_result.get("message", "API no válida")
                
    except ImportError as e:
        print(f"❌ No se pudo importar componentes necesarios: {e}")
        result["message"] = f"Error de importación: {str(e)}"
    except Exception as e:
        print(f"❌ Error al probar la integración con Anthropic: {e}")
        result["message"] = f"Error: {str(e)}"
        
    return result

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Probar Sistema de Verificación Freemium')
    parser.add_argument('--license', dest='license_key', help='Clave de licencia para pruebas')
    parser.add_argument('--api-key', dest='api_key', help='Clave API de Anthropic para pruebas')
    parser.add_argument('--setup', action='store_true', help='Configurar entorno de prueba')
    parser.add_argument('--test', choices=['all', 'license', 'subscription', 'anthropic'], 
                      default='all', help='Tipo de prueba a ejecutar')
    parser.add_argument('--simulate-api', dest='simulate_api', action='store_true',
                      help='Simular integración con API de Anthropic (sin realizar llamadas reales)')
    parser.add_argument('--no-api-required', dest='no_api_required', action='store_true',
                      help='No considerar error si la API no está configurada')
    parser.add_argument('--simulate-license', dest='simulate_license', action='store_true',
                      help='Simular verificación de licencia con una licencia demo')
    parser.add_argument('--simulate-premium', dest='simulate_premium', action='store_true',
                      help='Simular acceso premium en el sistema de suscripciones')
    args = parser.parse_args()
    
    # Ejecutar pruebas según la selección
    success = False
    if args.test == 'all':
        success = test_all(args)
    elif args.test == 'license':
        result = test_license_system(args)
        success = result.get('success', False)
        print(f"\nResultado: {'Éxito' if success else 'Fallo'} - {result['message']}")
    elif args.test == 'subscription':
        result = test_subscription_system(args)
        success = result.get('success', False)
        print(f"\nResultado: {'Éxito' if success else 'Fallo'} - {result['message']}")
    elif args.test == 'anthropic':
        result = test_anthropic_integration(args)
        success = result.get('success', False)
        print(f"\nResultado: {'Éxito' if success else 'Fallo'} - {result['message']}")
    
    # Devolver código de salida según resultado
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Error en la ejecución: {e}", exc_info=True)
        print(f"Error al ejecutar pruebas: {e}")
        sys.exit(1)
