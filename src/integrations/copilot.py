#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de integración con la API de GitHub Copilot.

Este módulo maneja la comunicación con la API de GitHub Copilot, la verificación
de credenciales y la gestión de límites según el plan del usuario.
"""

import os
import json
from typing import Dict, Optional, Tuple, Union
import requests
from src.utils.config import ConfigManager
from src.utils.logger import get_logger

# Configurar logger
logger = get_logger()

# URL base para la API de GitHub Copilot
GITHUB_API_URL = "https://api.github.com"
COPILOT_API_URL = "https://api.githubcopilot.com"


class CopilotAPI:
    """Cliente para la API de GitHub Copilot."""

    def __init__(self, api_token: Optional[str] = None, config: Optional[ConfigManager] = None):
        """
        Inicializar cliente de GitHub Copilot.
        
        Args:
            api_token: Token de GitHub opcional. Si no se proporciona, se intentará leer desde la configuración.
            config: Objeto de configuración opcional. Si no se proporciona, se creará uno nuevo.
        """
        self.config = config or ConfigManager()
        self.api_token = api_token or self.config.get("api.github.token")
        
        # Variables para control de uso y estado
        self._valid_token = False
        self._copilot_enabled = False
        self._user_info = {}

    @property
    def is_configured(self) -> bool:
        """Comprobar si la API está correctamente configurada."""
        return bool(self.api_token)
    
    def verify_api_token(self) -> Tuple[bool, str]:
        """
        Verificar si el token de GitHub es válido y tiene acceso a Copilot.
        
        Returns:
            Tupla con (éxito, mensaje)
        """
        if not self.api_token:
            logger.warning("No se ha configurado un token de GitHub")
            return False, "No se ha configurado un token de GitHub"
        
        # Verificar el token con la API de GitHub
        headers = self._get_headers()
        
        try:
            # Verificar que el token es válido obteniendo info del usuario
            user_response = requests.get(
                f"{GITHUB_API_URL}/user",
                headers=headers
            )
            
            if user_response.status_code != 200:
                error_msg = f"Token de GitHub inválido: {user_response.status_code} - {user_response.text}"
                logger.error(error_msg)
                return False, error_msg
                
            user_data = user_response.json()
            self._user_info = {
                "login": user_data.get("login"),
                "name": user_data.get("name"),
                "id": user_data.get("id"),
                "type": user_data.get("type")
            }
            
            # En una implementación real, verificaríamos si el usuario tiene acceso a Copilot
            # (GitHub no expone una API pública para esto, así que es simulado)
            
            # Simular verificación de suscripción a Copilot
            self._valid_token = True
            self._copilot_enabled = True
            
            logger.info(f"Token de GitHub verificado correctamente para {user_data.get('login')}")
            return True, "Token de GitHub válido con acceso a Copilot"
                
        except Exception as e:
            error_msg = f"Error al conectar con la API de GitHub: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _get_headers(self) -> Dict[str, str]:
        """Obtener los encabezados necesarios para las solicitudes a la API."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def get_usage_info(self) -> Dict[str, Union[bool, Dict]]:
        """
        Obtener información de uso de Copilot.
        
        Returns:
            Diccionario con información de la suscripción y usuario
        """
        # En una implementación real, consultaríamos la API
        # Devolvemos datos simulados por ahora
        return {
            "valid": self._valid_token,
            "copilot_enabled": self._copilot_enabled,
            "user": self._user_info
        }
        
    def set_api_token(self, api_token: str) -> bool:
        """
        Establecer un nuevo token de GitHub y guardarlo en la configuración.
        
        Args:
            api_token: El nuevo token de API
            
        Returns:
            True si el token se guardó correctamente
        """
        self.api_token = api_token
        self.config.set("api.github.token", api_token)
        self.config.save()
        return True


def get_copilot_client(config: Optional[ConfigManager] = None) -> CopilotAPI:
    """
    Obtener una instancia configurada del cliente de GitHub Copilot.
    
    Args:
        config: Objeto de configuración opcional
    
    Returns:
        Instancia de CopilotAPI
    """
    return CopilotAPI(config=config)
