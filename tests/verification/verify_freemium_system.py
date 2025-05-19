#!/usr/bin/env python3
"""
Script para verificar la implementación del Sistema de Verificación Freemium.
Este script comprueba todos los componentes del sistema de verificación freemium,
validando que estén correctamente implementados según la documentación.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("freemium_verifier")

# Intentamos importar los módulos del proyecto
try:
    from src.utils.license_validator import LicenseValidator
    from src.utils.subscription_manager import SubscriptionManager
    from src.utils.api_validator import APIValidator
    PROJECT_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"No se pueden importar los módulos del proyecto: {e}")
    PROJECT_MODULES_AVAILABLE = False


class FreemiumSystemVerifier:
    """Clase para verificar el sistema freemium."""
    
    def __init__(self, config_path: Optional[str] = None, simulate=None):
        """
        Inicializa el verificador.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
            simulate: Opciones de simulación (argparse.Namespace)
        """
        self.config_path = config_path
        self.verification_results = {}
        self.simulate = simulate or argparse.Namespace(
            simulate_api=False, 
            simulate_license=False, 
            simulate_premium=False
        )
        
    def verify_all(self) -> Dict[str, Any]:
        """
        Ejecuta todas las verificaciones del sistema freemium.
        
        Returns:
            Diccionario con los resultados de las verificaciones
        """
        logger.info("Iniciando verificación completa del sistema freemium...")
        
        # Lista de verificaciones a realizar
        verifications = [
            self.verify_license_validator,
            self.verify_subscription_manager,
            self.verify_api_integration,
            self.verify_freemium_limits,
            self.verify_config_system,
        ]
        
        # Ejecutar todas las verificaciones
        for verification in verifications:
            try:
                verification()
            except Exception as e:
                logger.error(f"Error en {verification.__name__}: {e}")
                self.verification_results[verification.__name__] = {
                    "status": "error",
                    "message": str(e)
                }
        
        # Resumen final
        self._print_summary()
        return self.verification_results
    
    def verify_license_validator(self) -> Dict[str, Any]:
        """
        Verifica el validador de licencias.
        
        Returns:
            Resultado de la verificación
        """
        logger.info("Verificando validador de licencias...")
        result = {
            "status": "pending",
            "components": {},
            "message": ""
        }
        
        # Si estamos en modo simulación, devolver éxito
        if self.simulate.simulate_license:
            logger.info("[SIMULACIÓN] Simulando validador de licencias")
            result["status"] = "success"
            result["message"] = "[SIMULACIÓN] Validador de licencias implementado correctamente"
            result["components"] = {
                "class_exists": True,
                "methods": {
                    "validate_license": True,
                    "_verify_online": True,
                    "_verify_offline": True
                },
                "hybrid_implementation": True
            }
            self.verification_results["verify_license_validator"] = result
            return result
        
        if not PROJECT_MODULES_AVAILABLE:
            result["status"] = "skipped"
            result["message"] = "Módulos del proyecto no disponibles"
            self.verification_results["verify_license_validator"] = result
            return result
        
        try:
            # Verificar que existe la clase LicenseValidator
            validator = LicenseValidator()
            result["components"]["class_exists"] = True
            
            # Verificar métodos críticos
            methods_to_check = [
                "validate_license",
                "_verify_online",
                "_verify_offline"
            ]
            
            result["components"]["methods"] = {}
            for method in methods_to_check:
                result["components"]["methods"][method] = hasattr(validator, method)
            
            # Verificar implementación de licencia híbrida
            has_hybrid = hasattr(validator, "_last_online_check")
            result["components"]["hybrid_implementation"] = has_hybrid
            
            # Determinar estado general
            if all(result["components"]["methods"].values()) and has_hybrid:
                result["status"] = "success"
                result["message"] = "Validador de licencias implementado correctamente"
            else:
                result["status"] = "warning"
                result["message"] = "Validador de licencias parcialmente implementado"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error al verificar el validador de licencias: {e}"
        
        self.verification_results["verify_license_validator"] = result
        return result
    
    def verify_subscription_manager(self) -> Dict[str, Any]:
        """
        Verifica el gestor de suscripciones.
        
        Returns:
            Resultado de la verificación
        """
        logger.info("Verificando gestor de suscripciones...")
        result = {
            "status": "pending",
            "components": {},
            "message": ""
        }
        
        # Si estamos en modo simulación, devolver éxito
        if getattr(self.simulate, 'simulate_premium', False):
            logger.info("[SIMULACIÓN] Simulando gestor de suscripciones")
            result["status"] = "success"
            result["message"] = "[SIMULACIÓN] Gestor de suscripciones implementado correctamente"
            result["components"] = {
                "class_exists": True,
                "methods": {
                    "is_premium_feature_available": True,
                    "get_subscription_type": True,
                    "increment_usage_count": True
                },
                "subscription_types": {
                    "free": True,
                    "basic": True,
                    "pro": True,
                    "team": True
                }
            }
            self.verification_results["verify_subscription_manager"] = result
            return result
        
        if not PROJECT_MODULES_AVAILABLE:
            result["status"] = "skipped"
            result["message"] = "Módulos del proyecto no disponibles"
            self.verification_results["verify_subscription_manager"] = result
            return result
        
        try:
            # Verificar que existe la clase SubscriptionManager
            manager = SubscriptionManager()
            result["components"]["class_exists"] = True
            
            # Verificar métodos críticos
            methods_to_check = [
                "is_premium_feature_available",
                "get_subscription_type",
                "increment_usage_count"
            ]
            
            result["components"]["methods"] = {}
            for method in methods_to_check:
                result["components"]["methods"][method] = hasattr(manager, method)
            
            # Verificar tipos de suscripción
            subscription_types = [
                "free", "basic", "pro", "team"
            ]
            
            from src.utils.subscription_manager import (
                SUBSCRIPTION_FREE, 
                SUBSCRIPTION_BASIC,
                SUBSCRIPTION_PRO,
                SUBSCRIPTION_TEAM
            )
            
            result["components"]["subscription_types"] = {
                "free": SUBSCRIPTION_FREE == "free",
                "basic": SUBSCRIPTION_BASIC == "basic",
                "pro": SUBSCRIPTION_PRO == "pro",
                "team": SUBSCRIPTION_TEAM == "team",
            }
            
            # Determinar estado general
            if (all(result["components"]["methods"].values()) and 
                all(result["components"]["subscription_types"].values())):
                result["status"] = "success"
                result["message"] = "Gestor de suscripciones implementado correctamente"
            else:
                result["status"] = "warning"
                result["message"] = "Gestor de suscripciones parcialmente implementado"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error al verificar el gestor de suscripciones: {e}"
        
        self.verification_results["verify_subscription_manager"] = result
        return result
    
    def verify_api_integration(self) -> Dict[str, Any]:
        """
        Verifica la integración con APIs externas.
        
        Returns:
            Resultado de la verificación
        """
        logger.info("Verificando integración con APIs externas...")
        result = {
            "status": "pending",
            "components": {},
            "message": ""
        }
        
        # Si estamos en modo simulación, devolver éxito
        if getattr(self.simulate, 'simulate_api', False):
            logger.info("[SIMULACIÓN] Simulando integración con APIs")
            result["status"] = "success"
            result["message"] = "[SIMULACIÓN] Integración con APIs implementada correctamente"
            result["components"] = {
                "api_validator_exists": True,
                "methods": {
                    "validate_api": True,
                    "set_api_key": True
                },
                "integrations": {
                    "anthropic": True
                }
            }
            self.verification_results["verify_api_integration"] = result
            return result
        
        if not PROJECT_MODULES_AVAILABLE:
            result["status"] = "skipped"
            result["message"] = "Módulos del proyecto no disponibles"
            self.verification_results["verify_api_integration"] = result
            return result
        
        try:
            # Verificar que existe el validador de APIs
            from src.utils.api_validator import get_api_validator
            validator = get_api_validator()
            result["components"]["api_validator_exists"] = True
            
            # Verificar métodos críticos
            methods_to_check = [
                "validate_api",
                "set_api_key"
            ]
            
            result["components"]["methods"] = {}
            for method in methods_to_check:
                result["components"]["methods"][method] = hasattr(validator, method)
            
            # Verificar integraciones específicas
            integrations = [
                "anthropic"
            ]
            
            result["components"]["integrations"] = {}
            for integration in integrations:
                is_supported = integration in getattr(validator, "available_apis", {})
                result["components"]["integrations"][integration] = is_supported
            
            # Determinar estado general
            if (all(result["components"]["methods"].values()) and 
                all(result["components"]["integrations"].values())):
                result["status"] = "success"
                result["message"] = "Integración con APIs implementada correctamente"
            else:
                result["status"] = "warning"
                result["message"] = "Integración con APIs parcialmente implementada"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error al verificar la integración con APIs: {e}"
        
        self.verification_results["verify_api_integration"] = result
        return result
    
    def verify_freemium_limits(self) -> Dict[str, Any]:
        """
        Verifica los límites del sistema freemium.
        
        Returns:
            Resultado de la verificación
        """
        logger.info("Verificando límites del sistema freemium...")
        result = {
            "status": "pending",
            "components": {},
            "message": ""
        }
        
        # Si estamos en modo simulación, devolver éxito
        if getattr(self.simulate, 'simulate_premium', False) or getattr(self.simulate, 'simulate_license', False):
            logger.info("[SIMULACIÓN] Simulando límites del sistema freemium")
            result["status"] = "success"
            result["message"] = "[SIMULACIÓN] Límites del sistema freemium configurados correctamente"
            result["components"] = {
                "limits_exist": True,
                "subscription_limits": {
                    "free": True,
                    "basic": True,
                    "pro": True,
                    "team": True
                },
                "premium_validation": True
            }
            self.verification_results["verify_freemium_limits"] = result
            return result
        
        if not PROJECT_MODULES_AVAILABLE:
            result["status"] = "skipped"
            result["message"] = "Módulos del proyecto no disponibles"
            self.verification_results["verify_freemium_limits"] = result
            return result
        
        try:
            # Verificar límites de uso
            from src.utils.subscription_manager import SUBSCRIPTION_LIMITS
            result["components"]["limits_exist"] = isinstance(SUBSCRIPTION_LIMITS, dict)
            
            # Verificar que existen límites para cada tipo de suscripción
            subscription_types = [
                "free", "basic", "pro", "team"
            ]
            
            result["components"]["subscription_limits"] = {}
            for sub_type in subscription_types:
                has_limits = sub_type in SUBSCRIPTION_LIMITS
                result["components"]["subscription_limits"][sub_type] = has_limits
            
            # Verificar integración con sistema de IA
            try:
                from src.integrations.anthropic_advanced import AdvancedAnthropicClient
                client = AdvancedAnthropicClient()
                result["components"]["premium_validation"] = hasattr(client, "verify_premium_access")
            except ImportError:
                result["components"]["premium_validation"] = False
            
            # Determinar estado general
            if (result["components"]["limits_exist"] and 
                all(result["components"]["subscription_limits"].values()) and
                result["components"]["premium_validation"]):
                result["status"] = "success"
                result["message"] = "Límites del sistema freemium configurados correctamente"
            else:
                result["status"] = "warning"
                result["message"] = "Límites del sistema freemium parcialmente configurados"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error al verificar los límites del sistema freemium: {e}"
        
        self.verification_results["verify_freemium_limits"] = result
        return result
    
    def verify_config_system(self) -> Dict[str, Any]:
        """
        Verifica el sistema de configuración para licencias.
        
        Returns:
            Resultado de la verificación
        """
        logger.info("Verificando sistema de configuración...")
        result = {
            "status": "pending",
            "components": {},
            "message": ""
        }
        
        # Si estamos en modo simulación, devolver éxito
        if getattr(self.simulate, 'simulate_api', False):
            logger.info("[SIMULACIÓN] Simulando sistema de configuración")
            result["status"] = "success"
            result["message"] = "[SIMULACIÓN] Sistema de configuración configurado correctamente"
            result["components"] = {
                "config_dir_exists": True,
                "config_file_exists": True,
                "anthropic_script_exists": True
            }
            self.verification_results["verify_config_system"] = result
            return result
        
        # Verificar archivo de configuración
        config_dir = os.path.expanduser("~/.config/project-prompt")
        config_file = os.path.join(config_dir, "config.yaml")
        result["components"]["config_dir_exists"] = os.path.exists(config_dir)
        result["components"]["config_file_exists"] = os.path.exists(config_file)
        
        # Verificar script de configuración de Anthropic
        script_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_anthropic_key.py")
        result["components"]["anthropic_script_exists"] = os.path.exists(script_file)
        
        # Determinar estado general
        if (result["components"]["config_dir_exists"] and
            result["components"]["config_file_exists"] and
            result["components"]["anthropic_script_exists"]):
            result["status"] = "success"
            result["message"] = "Sistema de configuración configurado correctamente"
        elif result["components"]["anthropic_script_exists"]:
            result["status"] = "warning"
            result["message"] = "Sistema de configuración parcialmente configurado (falta configuración)"
        else:
            result["status"] = "warning"
            result["message"] = "Sistema de configuración parcialmente configurado (faltan scripts)"
        
        self.verification_results["verify_config_system"] = result
        return result
        
    def _print_summary(self) -> None:
        """Imprime un resumen de las verificaciones."""
        print("\n" + "=" * 60)
        print("RESUMEN DE VERIFICACIÓN DEL SISTEMA FREEMIUM")
        print("=" * 60)
        
        total = len(self.verification_results)
        success = sum(1 for r in self.verification_results.values() if r.get("status") == "success")
        warnings = sum(1 for r in self.verification_results.values() if r.get("status") == "warning")
        errors = sum(1 for r in self.verification_results.values() if r.get("status") == "error")
        skipped = sum(1 for r in self.verification_results.values() if r.get("status") == "skipped")
        
        print(f"Total de verificaciones: {total}")
        print(f"✅ Exitosas: {success}")
        print(f"⚠️ Advertencias: {warnings}")
        print(f"❌ Errores: {errors}")
        print(f"⏭️ Omitidas: {skipped}")
        print("-" * 60)
        
        for name, result in self.verification_results.items():
            status_icon = {
                "success": "✅",
                "warning": "⚠️",
                "error": "❌",
                "skipped": "⏭️",
                "pending": "⏳"
            }.get(result.get("status", "pending"), "?")
            
            print(f"{status_icon} {name}: {result.get('message', 'Sin mensaje')}")
        
        print("=" * 60)
        
        # Lista de tareas pendientes en caso de haber advertencias o errores
        if warnings > 0 or errors > 0:
            print("\nTAREAS PENDIENTES PARA COMPLETAR LA IMPLEMENTACIÓN:")
            
            if not self._check_component_exists("verify_api_integration", "components", "api_validator_exists"):
                print("- Implementar APIValidator para la verificación de claves API")
                
            if not self._check_component_exists("verify_license_validator", "components", "hybrid_implementation"):
                print("- Implementar mecanismo híbrido (online/offline) para validación de licencias")
                
            if not self._check_component_method("verify_subscription_manager", "is_premium_feature_available"):
                print("- Implementar método is_premium_feature_available() en SubscriptionManager")
                
            if not self._check_component_exists("verify_freemium_limits", "components", "limits_exist"):
                print("- Definir límites de uso para cada tipo de suscripción")
                
            if not self._check_component_exists("verify_freemium_limits", "components", "premium_validation"):
                print("- Integrar validación premium con clientes de IA")
                
            if not self._check_component_exists("verify_config_system", "components", "config_file_exists"):
                print("- Crear archivo de configuración inicial")
                
        print()
    
    def _check_component_exists(self, verification, *path) -> bool:
        """Comprueba si un componente existe en los resultados."""
        if verification not in self.verification_results:
            return False
            
        result = self.verification_results[verification]
        for key in path:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return False
                
        return bool(result)
    
    def _check_component_method(self, verification, method) -> bool:
        """Comprueba si un método existe en un componente verificado."""
        return self._check_component_exists(verification, "components", "methods", method)
        

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Verificar el sistema de verificación freemium')
    parser.add_argument('--config', help='Ruta al archivo de configuración')
    parser.add_argument('--simulate-api', dest='simulate_api', action='store_true',
                      help='Simular integración con API de Anthropic (sin realizar llamadas reales)')
    parser.add_argument('--simulate-license', dest='simulate_license', action='store_true',
                      help='Simular verificación de licencia con una licencia demo')
    parser.add_argument('--simulate-premium', dest='simulate_premium', action='store_true',
                      help='Simular acceso premium en el sistema de suscripciones')
    parser.add_argument('--simulate', action='store_true',
                      help='Activar todos los modos de simulación')
    args = parser.parse_args()
    
    # Si se activa --simulate, activar todas las opciones de simulación
    if args.simulate:
        args.simulate_api = True
        args.simulate_license = True
        args.simulate_premium = True
    
    verifier = FreemiumSystemVerifier(config_path=args.config, simulate=args)
    results = verifier.verify_all()
    
    # Determinar código de salida según resultados
    all_passed = all(r.get("status") == "success" for r in results.values() if "status" in r)
    sys.exit(0 if all_passed else 1)
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error executing the verification: {e}")
        import traceback
        traceback.print_exc()
