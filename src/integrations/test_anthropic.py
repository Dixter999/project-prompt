#!/usr/bin/env python3
"""
Módulo para probar la integración con Anthropic API.
Este módulo proporciona una función simple para verificar que la API de Anthropic
está correctamente configurada y funcionando con el sistema de verificación freemium.
"""

import os
import sys
from typing import Dict, Any, Optional, Tuple
import logging

from src.utils.logger import get_logger
# Premium features now available for all users
from src.integrations.anthropic import get_anthropic_client
from src.integrations.anthropic_advanced import get_advanced_anthropic_client

# Configurar logger
logger = get_logger()

def test_anthropic_integration() -> Tuple[bool, Dict[str, Any]]:
    """
    Prueba la integración con la API de Anthropic.
    
    Returns:
        Una tupla con (éxito, resultados)
    """
    results = {
        "success": False,
        "status": {
            "api_configured": False,
            "api_key_valid": False,
            "premium_access": False,
            "response_received": False
        },
        "message": "",
        "details": {},
        "test_response": None
    }
    
    # Paso 1: Verificar configuración del cliente Anthropic
    try:
        client = get_anthropic_client()
        results["status"]["api_configured"] = client.is_configured
        
        if not client.is_configured:
            results["message"] = "API de Anthropic no configurada. Use el comando 'project-prompt set_api anthropic' para configurarla."
            return False, results
            
        logger.info("Cliente de Anthropic configurado correctamente")
    except Exception as e:
        logger.error(f"Error al obtener cliente Anthropic: {e}")
        results["message"] = f"Error al inicializar cliente Anthropic: {str(e)}"
        return False, results
    
    # Paso 2: Verificar validez de la clave API
    try:
        success, message = client.verify_api_key()
        results["status"]["api_key_valid"] = success
        
        if not success:
            results["message"] = f"Clave API de Anthropic no válida: {message}"
            return False, results
            
        logger.info("Clave API de Anthropic verificada correctamente")
    except Exception as e:
        logger.error(f"Error al verificar clave API: {e}")
        results["message"] = f"Error al verificar clave API: {str(e)}"
        return False, results
    
    # Paso 3: Verificar acceso premium - ahora disponible para todos los usuarios
    try:
        # Premium features now available for all users
        premium_access = True
        results["status"]["premium_access"] = premium_access
        
        logger.info("Premium features now available for all users")
    except Exception as e:
        logger.warning(f"Error al verificar estado de suscripción: {e}")
        # Seguimos aunque no podamos verificar el acceso premium
    
    # Paso 4: Realizar una prueba simple con la API
    try:
        # Intentar una consulta simple a Claude
        response = client.simple_completion(
            "Responde en una sola palabra: ¿Funciona la integración?",
            max_tokens=10
        )
        
        results["status"]["response_received"] = True
        results["test_response"] = response
        
        logger.info("Prueba con API de Anthropic completada correctamente")
    except Exception as e:
        logger.error(f"Error al realizar prueba con la API: {e}")
        results["message"] = f"Error al realizar prueba con la API: {str(e)}"
        results["status"]["response_received"] = False
        # No retornamos error aquí, queremos mostrar el resultado hasta donde llegamos
    
    # Evaluación final
    all_required_checks = (
        results["status"]["api_configured"] and
        results["status"]["api_key_valid"] and
        results["status"]["response_received"]
    )
    
    results["success"] = all_required_checks
    
    if all_required_checks:
        results["message"] = "Integración con Anthropic validada correctamente"
    elif not results["message"]:
        # Si no tenemos un mensaje de error específico pero falló
        results["message"] = "No se pudo completar todas las verificaciones"
    
    return results["success"], results


def get_anthropic_status_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen del estado de integración con Anthropic.
    
    Returns:
        Diccionario con el resumen de estado
    """
    try:
        success, results = test_anthropic_integration()
        
        return {
            "configured": results["status"]["api_configured"],
            "valid_key": results["status"]["api_key_valid"],
            "premium_access": results["status"]["premium_access"],
            "operational": results["status"]["response_received"],
            "success": success,
            "message": results["message"]
        }
    except Exception as e:
        logger.error(f"Error al obtener resumen de estado Anthropic: {e}")
        return {
            "configured": False,
            "valid_key": False,
            "premium_access": False,
            "operational": False,
            "success": False,
            "message": f"Error al verificar estado: {str(e)}"
        }


if __name__ == "__main__":
    # Ejecutar prueba independiente
    success, results = test_anthropic_integration()
    
    if success:
        print("✅ Integración con Anthropic validada correctamente")
    else:
        print(f"❌ Error en la integración con Anthropic: {results['message']}")
    
    # Mostrar detalles
    print("\nDetalles de la verificación:")
    for key, value in results["status"].items():
        status = "✅" if value else "❌"
        print(f"{status} {key}")
    
    # Mostrar respuesta si la hay
    if results["test_response"]:
        print("\nRespuesta de prueba de Claude:")
        print(results["test_response"])
