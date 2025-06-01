#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la validación de claves de API.

Este módulo proporciona funciones para validar, almacenar y gestionar
claves de API para diferentes servicios (OpenAI, Anthropic, GitHub Copilot, etc.).
"""

import os
import json
import keyring
from typing import Dict, List, Optional, Tuple, Union
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.config import ConfigManager
from src.utils.logger import get_logger

# Lazy imports to avoid circular imports
def _get_anthropic_client():
    """Lazy import to avoid circular dependency"""
    from src.integrations.anthropic import get_anthropic_client
    return get_anthropic_client()

def _get_copilot_client():
    """Lazy import to avoid circular dependency"""
    from src.integrations.copilot import get_copilot_client
    return get_copilot_client()

# Configurar logger
logger = get_logger()

# Para pruebas en entornos sin keyring
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    from ..utils.mock_keyring import MockKeyring
    keyring = MockKeyring()
    KEYRING_AVAILABLE = False


class APIValidator:
    """Validador de claves de API para diferentes servicios."""

    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar el validador de APIs.
        
        Args:
            config: Objeto de configuración opcional
        """
        self.config = config or ConfigManager()
        self.available_apis = {
            "anthropic": self._check_anthropic,
            "github": self._check_github,
        }
        self._api_clients = {}
        self._api_status = {}
        
    def validate_all_apis(self) -> Dict[str, Dict]:
        """
        Validar todas las APIs configuradas.
        
        Returns:
            Diccionario con estado de cada API
        """
        logger.info("Validando todas las claves de API configuradas...")
        results = {}
        
        # Validar APIs en paralelo para mayor eficiencia
        with ThreadPoolExecutor(max_workers=len(self.available_apis)) as executor:
            future_to_api = {
                executor.submit(self.validate_api, api_name): api_name 
                for api_name in self.available_apis
            }
            
            for future in as_completed(future_to_api):
                api_name = future_to_api[future]
                try:
                    results[api_name] = future.result()
                except Exception as exc:
                    logger.error(f"Error al validar API {api_name}: {exc}")
                    results[api_name] = {
                        "valid": False,
                        "message": f"Error al validar: {str(exc)}"
                    }
        
        # Guardar resultados
        self._api_status = results
        return results
        
    def validate_api(self, api_name: str) -> Dict:
        """
        Validar una API específica.
        
        Args:
            api_name: Nombre de la API a validar
            
        Returns:
            Diccionario con información de estado
        """
        if api_name not in self.available_apis:
            logger.warning(f"API no soportada: {api_name}")
            return {
                "valid": False,
                "message": f"API no soportada: {api_name}"
            }
            
        # Ejecutar el validador correspondiente
        validator_func = self.available_apis[api_name]
        return validator_func()
        
    def _check_anthropic(self) -> Dict:
        """
        Validar la configuración de la API de Anthropic.
        
        Returns:
            Diccionario con estado y mensaje
        """
        client = _get_anthropic_client()
        self._api_clients["anthropic"] = client
        
        if not client.is_configured:
            return {
                "valid": False,
                "message": "No se ha configurado una clave API para Anthropic",
                "configured": False
            }
            
        valid, message = client.verify_api_key()
        usage_info = client.get_usage_info()
        
        return {
            "valid": valid,
            "message": message,
            "configured": True,
            "usage": usage_info
        }
        
    def _check_github(self) -> Dict:
        """
        Validar la configuración de la API de GitHub Copilot.
        
        Returns:
            Diccionario con estado y mensaje
        """
        client = _get_copilot_client()
        self._api_clients["github"] = client
        
        if not client.is_configured:
            return {
                "valid": False,
                "message": "No se ha configurado un token para GitHub Copilot",
                "configured": False
            }
            
        valid, message = client.verify_api_token()
        usage_info = client.get_usage_info()
        
        return {
            "valid": valid,
            "message": message,
            "configured": True,
            "usage": usage_info
        }
    
    def set_api_key(self, api_name: str, api_key: str) -> Tuple[bool, str]:
        """
        Establecer o actualizar una clave de API.
        
        Args:
            api_name: Nombre de la API ("anthropic", "github", etc.)
            api_key: Nueva clave o token
            
        Returns:
            Tuple de (éxito, mensaje)
        """
        if api_name not in self.available_apis:
            return False, f"API no soportada: {api_name}"
            
        try:
            # Almacenar en keyring si está disponible
            if KEYRING_AVAILABLE:
                keyring.set_password("project_prompt", f"api_{api_name}", api_key)
                logger.info(f"Clave para {api_name} almacenada en keyring")
                
            # Actualizar en el cliente correspondiente
            if api_name == "anthropic":
                if "anthropic" not in self._api_clients:
                    self._api_clients["anthropic"] = _get_anthropic_client()
                self._api_clients["anthropic"].set_api_key(api_key)
                
            elif api_name == "github":
                if "github" not in self._api_clients:
                    self._api_clients["github"] = _get_copilot_client()
                self._api_clients["github"].set_api_token(api_key)
                
            # Validar la nueva clave
            validation = self.validate_api(api_name)
            if validation["valid"]:
                return True, f"Clave para {api_name} configurada y validada correctamente"
            else:
                return False, f"Clave para {api_name} guardada, pero no es válida: {validation['message']}"
                
        except Exception as e:
            logger.error(f"Error al establecer clave para {api_name}: {str(e)}")
            return False, f"Error al establecer clave: {str(e)}"
            
    def get_status_summary(self) -> Dict[str, bool]:
        """
        Obtener un resumen del estado de las APIs.
        
        Returns:
            Diccionario con el estado de cada API
        """
        # Si no tenemos datos de estado, validamos todas las APIs primero
        if not self._api_status:
            self.validate_all_apis()
            
        summary = {}
        for api, status in self._api_status.items():
            summary[api] = status.get("valid", False)
            
        return summary
        

def get_api_validator(config: Optional[ConfigManager] = None) -> APIValidator:
    """
    Obtener una instancia del validador de APIs.
    
    Args:
        config: Objeto de configuración opcional
        
    Returns:
        Instancia de APIValidator
    """
    return APIValidator(config=config)
