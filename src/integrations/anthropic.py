#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de integración con la API de Anthropic (Claude).

Este módulo maneja la comunicación con la API de Anthropic, la verificación
de credenciales y la gestión de límites según el plan del usuario.
"""

import os
from typing import Any, Dict, Optional, Tuple, Union
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
        self.api_key = api_key or self.config.get_api_key("anthropic")
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
        
    def set_api_key(self, api_key: str) -> None:
        """
        Establece o actualiza la clave API.
        
        Args:
            api_key: Nueva clave API para Anthropic
        """
        self.api_key = api_key
        
        # Actualizar en la configuración
        if self.config:
            self.config.set("api.anthropic.key", api_key)
            self.config.set("api.anthropic.enabled", True)
            self.config.save_config()
        
        # Resetear estado de validación
        self._valid_key = False

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
        Obtiene información de uso de la API.
        
        Returns:
            Dict con información de uso
        """
        return {
            "limit": self._usage_limit,
            "used": self._usage_current,
            "remaining": max(0, self._usage_limit - self._usage_current),
            "valid_key": self._valid_key
        }
        
    def simple_completion(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Realiza una consulta simple a la API de Claude y retorna la respuesta como texto.
        
        Args:
            prompt: Texto de la consulta
            max_tokens: Número máximo de tokens en la respuesta (opcional)
            
        Returns:
            Texto de la respuesta
            
        Raises:
            Exception: Si hay un error en la API o no está configurada
        """
        if not self.is_configured:
            raise ValueError("API de Anthropic no configurada. Configure una clave API primero.")
            
        # Establecer número máximo de tokens
        tokens = max_tokens or self.max_tokens
        
        # Preparar payload
        payload = {
            "model": self.model,
            "max_tokens": min(tokens, 4096),  # Límite de seguridad
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Realizar la solicitud
        try:
            response = requests.post(
                f"{ANTHROPIC_API_BASE_URL}/v1/messages",
                headers=self._get_headers(),
                json=payload
            )
            
            # Verificar si hay error
            if response.status_code != 200:
                error_msg = f"Error en API Anthropic: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            # Procesar respuesta
            result = response.json()
            content = result.get("content", [])
            
            # Extraer el texto del contenido
            text_parts = []
            for item in content:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                    
            return "".join(text_parts).strip()
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión con API Anthropic: {e}")
            raise Exception(f"Error de conexión: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error al procesar respuesta de Anthropic: {e}")
            raise

    def generate_text(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text using Claude API with structured response.
        
        Args:
            prompt: Text prompt for the AI
            max_tokens: Maximum tokens in response (optional)
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Dict with 'content' key containing the response text and metadata
            
        Raises:
            Exception: If API is not configured or request fails
        """
        if not self.is_configured:
            raise ValueError("API de Anthropic no configurada. Configure una clave API primero.")
            
        # Establecer número máximo de tokens
        tokens = max_tokens or self.max_tokens
        
        # Preparar payload
        payload = {
            "model": self.model,
            "max_tokens": min(tokens, 4096),  # Límite de seguridad
            "temperature": max(0.0, min(1.0, temperature)),  # Clamp temperature
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Realizar la solicitud
        try:
            response = requests.post(
                f"{ANTHROPIC_API_BASE_URL}/v1/messages",
                headers=self._get_headers(),
                json=payload
            )
            
            # Verificar si hay error
            if response.status_code != 200:
                error_msg = f"Error en API Anthropic: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            # Procesar respuesta
            result = response.json()
            content = result.get("content", [])
            
            # Extraer el texto del contenido
            text_parts = []
            for item in content:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                    
            response_text = "".join(text_parts).strip()
            
            # Retornar respuesta estructurada
            return {
                "content": response_text,
                "model": self.model,
                "usage": result.get("usage", {}),
                "stop_reason": result.get("stop_reason", "unknown")
            }
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión con API Anthropic: {e}")
            raise Exception(f"Error de conexión: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error al procesar respuesta de Anthropic: {e}")
            raise


def get_anthropic_client(config: Optional[ConfigManager] = None) -> AnthropicAPI:
    """
    Obtener una instancia configurada del cliente Anthropic.
    
    Args:
        config: Objeto de configuración opcional
    
    Returns:
        Instancia de AnthropicAPI
    """
    return AnthropicAPI(config=config)
