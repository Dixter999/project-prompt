#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el sistema de validación de APIs.

Este script prueba la funcionalidad básica del validador de APIs.
"""

import os
import sys
import json
from pathlib import Path

# Asegurar que podemos importar desde src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.api_validator import APIValidator, get_api_validator
from src.utils.config import Config


def test_api_validator():
    """Probar la funcionalidad del validador de APIs."""
    print("Probando el validador de APIs...")
    
    # Crear una instancia del validador
    validator = get_api_validator()
    
    # Verificar todas las APIs
    print("\nVerificando todas las APIs configuradas...")
    results = validator.validate_all_apis()
    
    # Mostrar resultados
    for api_name, status in results.items():
        valid = status.get("valid", False)
        message = status.get("message", "")
        configured = status.get("configured", False)
        
        status_str = "✓" if valid else "✗"
        config_str = "Configurada" if configured else "No configurada"
        
        print(f"{api_name}: {status_str} {config_str} - {message}")
        
        # Si hay información de uso, mostrarla
        if "usage" in status:
            for key, value in status["usage"].items():
                print(f"  - {key}: {value}")
    
    print("\nPrueba completada.")


if __name__ == "__main__":
    test_api_validator()
