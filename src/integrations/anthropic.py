#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de integración con la API de Anthropic (Claude).

Este módulo maneja la comunicación con la API de Anthropic, la verificación
de credenciales y la gestión de límites según el plan del usuario.
"""

import os
from typing import Dict, Optional, Tuple, Union
import logging
import requests
from src.utils.config import ConfigManager
from src.utils.logger import get_logger

# Configurar logger
logger = get_logger()

# URL base de la API de Anthropic
ANTHROPIC_API_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_API_VERSION = "2023-06-01"


class AnthropicAPI:
    """Cliente para la API de Anthropic (Claude)."""

    def __init__(self, api_key: Optional[str] = None, config: Optional[ConfigManager] = None):
        """
        Inicializar cliente de Anthropic.
        
        Args:
            api_key: Clave API opcional. Si no se proporciona, se intentará leer desde la configuración.
            config: Objeto de configuración opcional. Si no se proporciona, se creará uno nuevo.
        """
        self.config = config or ConfigManager()
        self.api_key = api_key or self.config.get("api.anthropic.key")
        self.max_tokens = self.config.get("api.anthropic.max_tokens", 4000)
        self.model = self.config.get("api.anthropic.model", "claude-3-haiku-20240307")
        
        # Variables para control de uso
        self._valid_key = False
        self._usage_limit = 0
        self._usage_current = 0

    @property
    def is_configured(self) -> bool:
        """Comprobar si la API está correctamente configurada."""
        return bool(self.api_key)
    
    def verify_api_key(self) -> Tuple[bool, str]:
        """
        Verificar si la clave API es válida.
        
        Returns:
            Tupla con (éxito, mensaje)
        """
        if not self.api_key:
            logger.warning("No se ha configurado una clave API para Anthropic")
            return False, "No se ha configurado una clave API para Anthropic"
        
        # Hacer una solicitud simple a la API para verificar la clave
        headers = self._get_headers()
        
        try:
            # Hacemos una solicitud mínima para verificar la clave
            response = requests.post(
                f"{ANTHROPIC_API_BASE_URL}/v1/messages",
                headers=headers,
                json={
                    "model": self.model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )
            
            if response.status_code == 200:
                self._valid_key = True
                logger.info("Clave API de Anthropic verificada correctamente")
                return True, "Clave API válida"
            else:
                error_msg = f"Error al verificar la clave API de Anthropic: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error al conectar con la API de Anthropic: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _get_headers(self) -> Dict[str, str]:
        """Obtener los encabezados necesarios para las solicitudes a la API."""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "content-type": "application/json"
        }

    def get_usage_info(self) -> Dict[str, Union[int, bool]]:
        """
        Obtener información de uso de la API.
        
        Returns:
            Diccionario con información de límites y uso actual
        """
        # En una implementación real, aquí consultaríamos a la API sobre los límites
        # Por ahora devolvemos valores simulados
        return {
            "valid": self._valid_key,
            "limit": self._usage_limit,
            "used": self._usage_current,
            "remaining": max(0, self._usage_limit - self._usage_current)
        }
        
    def set_api_key(self, api_key: str) -> bool:
        """
        Establecer una nueva clave API y guardarla en la configuración.
        
        Args:
            api_key: La nueva clave API
            
        Returns:
            True si la clave se guardó correctamente
        """
        self.api_key = api_key
        self.config.set("api.anthropic.key", api_key)
        self.config.save()
        return True


def get_anthropic_client(config: Optional[ConfigManager] = None) -> AnthropicAPI:
    """
    Obtener una instancia configurada del cliente Anthropic.
    
    Args:
        config: Objeto de configuración opcional
    
    Returns:
        Instancia de AnthropicAPI
    """
    return AnthropicAPI(config=config)
