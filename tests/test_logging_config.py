#!/usr/bin/env python3
"""
Script de prueba para el sistema de logging y configuración.
"""
from src.utils import (
    logger, debug, info, warning, error, critical, set_level, LogLevel,
    config_manager, set_config, get_config, set_api_key, get_api_key
)

def test_logging():
    """Prueba diferentes niveles de logging."""
    print("\n=== PRUEBA DE SISTEMA DE LOGGING ===")
    
    debug("Este es un mensaje de nivel DEBUG")
    info("Este es un mensaje de nivel INFO")
    warning("Este es un mensaje de nivel WARNING")
    error("Este es un mensaje de nivel ERROR")
    critical("Este es un mensaje de nivel CRITICAL")
    
    print("\n=== CAMBIO DE NIVEL DE LOG A DEBUG ===")
    set_level(LogLevel.DEBUG)
    debug("Ahora puedes ver los mensajes DEBUG")
    
    print("\n=== CAMBIO DE NIVEL DE LOG A WARNING ===")
    set_level(LogLevel.WARNING)
    debug("Este mensaje DEBUG no se mostrará")
    info("Este mensaje INFO no se mostrará")
    warning("Este mensaje WARNING sí se mostrará")

def test_config():
    """Prueba el sistema de configuración."""
    print("\n=== PRUEBA DE SISTEMA DE CONFIGURACIÓN ===")
    
    # Mostrar configuración actual
    print(f"Nivel de log actual: {get_config('log_level')}")
    
    # Cambiar y guardar configuración
    print("Cambiando nivel de log en configuración...")
    set_config('log_level', 'debug')
    print(f"Nuevo nivel de log: {get_config('log_level')}")
    
    # Configuración de API
    print("\n=== PRUEBA DE GESTIÓN DE CLAVES API ===")
    set_api_key('openai', 'sk-test-key-123456')
    print(f"API OpenAI habilitada: {get_config('api.openai.enabled')}")
    
    # Verificar estado premium
    print(f"Estado premium: {get_config('features.premium')}")

if __name__ == "__main__":
    print("EJECUTANDO PRUEBAS DEL SISTEMA DE LOGGING Y CONFIGURACIÓN")
    test_logging()
    test_config()
