#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de funcionalidades avanzadas para la API de Anthropic (Claude).

Este módulo extiende las capacidades básicas de integración con Anthropic,
proporcionando funcionalidades premium como generación de código específico,
detección de errores y sugerencias de refactorización.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import requests
import tiktoken

from src.integrations.anthropic import AnthropicAPI, get_anthropic_client, ANTHROPIC_API_BASE_URL, ANTHROPIC_API_VERSION
from src.utils.logger import get_logger
from src.utils.config import ConfigManager
from src.utils.prompt_optimizer import get_prompt_optimizer

# Configurar logger
logger = get_logger()


class AdvancedAnthropicClient:
    """Cliente avanzado para la API de Anthropic con capacidades premium."""

    def __init__(self, api_key: Optional[str] = None, config: Optional[ConfigManager] = None):
        """
        Inicializar cliente avanzado de Anthropic.
        
        Args:
            api_key: Clave API opcional
            config: Objeto de configuración opcional
        """
        self.config = config or ConfigManager()
        self.base_client = get_anthropic_client(config)
        # Premium features now available for all users
        self.prompt_optimizer = get_prompt_optimizer(config)
        
        # Modelos preferidos para tareas premium (configurables)
        self.code_model = self.config.get("api.anthropic.premium_model", "claude-3-opus-20240229")
        self.analysis_model = self.config.get("api.anthropic.analysis_model", "claude-3-sonnet-20240229")
    
    @property
    def is_configured(self) -> bool:
        """Comprobar si la API está correctamente configurada."""
        return self.base_client.is_configured
    
    def verify_premium_access(self) -> bool:
        """
        Verificar si el usuario tiene acceso a características premium.
        
        Returns:
            True si tiene acceso, False en caso contrario
        """
        # Verificar que el cliente base está configurado
        if not self.base_client.is_configured:
            logger.warning("Cliente de Anthropic no configurado para funciones premium")
            return False
        
        # Premium features now available for all users
        return True
    
    def generate_code(self, 
                     prompt: str, 
                     language: str, 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generar código específico utilizando Claude.
        
        Args:
            prompt: Descripción de lo que se necesita generar
            language: Lenguaje de programación objetivo
            context: Contexto adicional para la generación
            
        Returns:
            Diccionario con el código generado y metadatos
        """
        # Verificar acceso premium
        if not self.verify_premium_access():
            return {
                "success": False,
                "error": "Esta función requiere suscripción premium",
                "code": None
            }
        
        # Contexto por defecto
        context = context or {}
        context["language"] = language
        
        # Optimizar el prompt para generación de código
        optimized_prompt = self.prompt_optimizer.optimize(
            prompt, "anthropic", "code_generation", context
        )
        
        # Crear mensaje para enviar a la API
        messages = [{
            "role": "user",
            "content": f"Generate {language} code for the following task: {optimized_prompt}\n\nPlease provide only well-structured, production-ready {language} code with appropriate comments."
        }]
        
        try:
            # Realizar solicitud a la API
            response = self._make_api_request(
                messages=messages,
                model=self.code_model,
                max_tokens=4000
            )
            
            # Extraer código de la respuesta
            code = self._extract_code_from_response(response, language)
            
            return {
                "success": True,
                "code": code,
                "language": language,
                "model": self.code_model
            }
        
        except Exception as e:
            logger.error(f"Error al generar código: {str(e)}")
            return {
                "success": False,
                "error": f"Error al generar código: {str(e)}",
                "code": None
            }
    
    def detect_errors(self, 
                     code: str, 
                     language: str,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detectar errores en código existente.
        
        Args:
            code: Código a analizar
            language: Lenguaje del código
            context: Contexto adicional para el análisis
            
        Returns:
            Diccionario con errores detectados y sugerencias
        """
        # Verificar acceso premium
        if not self.verify_premium_access():
            return {
                "success": False,
                "error": "Esta función requiere suscripción premium",
                "issues": []
            }
        
        # Contexto por defecto
        context = context or {}
        context["language"] = language
        
        # Optimizar el prompt para detección de errores
        code_prompt = f"Analyze this {language} code for bugs, security issues, and inefficiencies:\n\n```{language}\n{code}\n```"
        optimized_prompt = self.prompt_optimizer.optimize(
            code_prompt, "anthropic", "error_detection", context
        )
        
        # Crear mensaje para enviar a la API
        messages = [{
            "role": "user", 
            "content": f"{optimized_prompt}\n\nPlease identify issues in this format for each problem:\n1. [Issue Type]: Brief description\n   - Location: Where in the code\n   - Severity: (High/Medium/Low)\n   - Fix: Suggested solution"
        }]
        
        try:
            # Realizar solicitud a la API
            response = self._make_api_request(
                messages=messages,
                model=self.analysis_model,
                max_tokens=2000
            )
            
            # Procesar respuesta para extraer los problemas detectados
            issues = self._extract_issues_from_response(response)
            
            return {
                "success": True,
                "issues": issues,
                "language": language,
                "model": self.analysis_model
            }
        
        except Exception as e:
            logger.error(f"Error al detectar errores: {str(e)}")
            return {
                "success": False,
                "error": f"Error al analizar código: {str(e)}",
                "issues": []
            }
    
    def suggest_refactoring(self, 
                          code: str, 
                          language: str,
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sugerir mejoras de refactorización para un código.
        
        Args:
            code: Código a refactorizar
            language: Lenguaje del código
            context: Contexto adicional para la refactorización
            
        Returns:
            Diccionario con sugerencias de refactorización
        """
        # Verificar acceso premium
        if not self.verify_premium_access():
            return {
                "success": False,
                "error": "Esta función requiere suscripción premium",
                "refactored_code": None,
                "suggestions": []
            }
        
        # Contexto por defecto
        context = context or {}
        context["language"] = language
        
        # Optimizar el prompt para sugerencias de refactorización
        code_prompt = f"Refactor this {language} code to improve its quality while maintaining functionality:\n\n```{language}\n{code}\n```"
        optimized_prompt = self.prompt_optimizer.optimize(
            code_prompt, "anthropic", "refactoring", context
        )
        
        # Crear mensaje para enviar a la API
        messages = [{
            "role": "user",
            "content": f"{optimized_prompt}\n\nPlease provide:\n1. An explanation of your refactoring approach\n2. The refactored code\n3. Key improvements made"
        }]
        
        try:
            # Realizar solicitud a la API
            response = self._make_api_request(
                messages=messages,
                model=self.code_model,
                max_tokens=4000
            )
            
            # Procesar respuesta
            refactored_code = self._extract_code_from_response(response, language)
            suggestions = self._extract_refactoring_suggestions(response)
            
            return {
                "success": True,
                "refactored_code": refactored_code,
                "suggestions": suggestions,
                "language": language,
                "model": self.code_model
            }
        
        except Exception as e:
            logger.error(f"Error al sugerir refactorización: {str(e)}")
            return {
                "success": False,
                "error": f"Error al generar sugerencias de refactorización: {str(e)}",
                "refactored_code": None,
                "suggestions": []
            }
    
    def explain_code(self, 
                    code: str, 
                    language: str,
                    detail_level: str = "standard",
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generar explicación detallada de un código.
        
        Args:
            code: Código a explicar
            language: Lenguaje del código
            detail_level: Nivel de detalle ('basic', 'standard', 'advanced')
            context: Contexto adicional
            
        Returns:
            Diccionario con la explicación
        """
        # Verificar acceso premium para nivel avanzado
        if detail_level == "advanced" and not self.verify_premium_access():
            detail_level = "standard"
            logger.info("Nivel de detalle avanzado requiere suscripción premium, usando nivel estándar")
        
        # Determinar el modelo basado en el nivel de detalle
        model = self.analysis_model
        if detail_level == "basic":
            model = self.base_client.model  # Modelo básico
        
        # Crear mensaje para enviar a la API
        messages = [{
            "role": "user",
            "content": f"Explain this {language} code:\n\n```{language}\n{code}\n```\n\nDetail level: {detail_level}"
        }]
        
        try:
            # Realizar solicitud a la API
            response = self._make_api_request(
                messages=messages,
                model=model,
                max_tokens=2000
            )
            
            return {
                "success": True,
                "explanation": response.get("content", ""),
                "language": language,
                "model": model,
                "detail_level": detail_level
            }
        
        except Exception as e:
            logger.error(f"Error al explicar código: {str(e)}")
            return {
                "success": False,
                "error": f"Error al explicar código: {str(e)}",
                "explanation": None
            }
    
    def _make_api_request(self, 
                        messages: List[Dict[str, str]], 
                        model: str, 
                        max_tokens: int) -> Dict[str, Any]:
        """
        Realizar una solicitud a la API de Anthropic.
        
        Args:
            messages: Lista de mensajes a enviar
            model: Modelo de Anthropic a utilizar
            max_tokens: Número máximo de tokens para la respuesta
            
        Returns:
            Respuesta de la API
        """
        import time
        
        # Logging detallado para debugging
        logger.info("====== ANTHROPIC API REQUEST DEBUG ======")
        logger.info(f"API Key configured: {'Yes' if self.base_client.api_key else 'No'}")
        logger.info(f"API Key (first 10 chars): {self.base_client.api_key[:10] if self.base_client.api_key else 'None'}...")
        logger.info(f"Model: {model}")
        logger.info(f"Max tokens: {max_tokens}")
        logger.info(f"Messages count: {len(messages)}")
        if messages:
            logger.info(f"First message preview: {messages[0]['content'][:200]}...")
        
        # Verificar que tengamos una clave API válida
        if not self.base_client.api_key:
            logger.error("No se ha configurado una clave API para Anthropic")
            raise ValueError("No se ha configurado una clave API para Anthropic")
        
        # Preparar headers
        headers = {
            "x-api-key": self.base_client.api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "content-type": "application/json"
        }
        
        # Preparar datos de la solicitud
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        url = f"{ANTHROPIC_API_BASE_URL}/v1/messages"
        logger.info(f"Making HTTP POST request to: {url}")
        
        # Timing de la solicitud
        start_time = time.time()
        
        # Realizar la solicitud
        try:
            response = requests.post(url, headers=headers, json=data)
            request_duration = time.time() - start_time
            
            logger.info(f"Request completed in {request_duration:.2f} seconds")
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            # Log response size
            if hasattr(response, 'content'):
                logger.info(f"Response content size: {len(response.content)} bytes")
            
        except Exception as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise
        
        # Verificar respuesta
        if response.status_code != 200:
            error_text = response.text[:500] if response.text else "No error text"
            logger.error(f"API returned non-200 status: {response.status_code}")
            logger.error(f"Error response text: {error_text}")
            error_info = response.json() if response.text else {"error": f"Status code: {response.status_code}"}
            raise Exception(f"Error en API Anthropic: {error_info}")
        
        try:
            response_data = response.json()
            logger.info(f"Response JSON keys: {list(response_data.keys()) if response_data else 'None'}")
            
            # Log usage info if available
            if "usage" in response_data:
                usage = response_data["usage"]
                logger.info(f"Token usage - Input: {usage.get('input_tokens', 'N/A')}, Output: {usage.get('output_tokens', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Failed to parse response JSON: {str(e)}")
            logger.error(f"Raw response text: {response.text[:500]}")
            raise
        
        # Extraer contenido de la respuesta
        if response_data and "content" in response_data:
            content = response_data["content"][0]["text"] if response_data["content"] else ""
            logger.info(f"Response content length: {len(content)} characters")
            logger.info(f"Response content preview: {content[:200]}...")
            logger.info("====== API REQUEST COMPLETED ======")
            return {"content": content, "raw_response": response_data}
        else:
            logger.error(f"Unexpected response format: {response_data}")
            raise Exception("Formato de respuesta inesperado de la API")
    
    def _extract_code_from_response(self, response: Dict[str, Any], language: str) -> str:
        """
        Extraer código de la respuesta de la API.
        
        Args:
            response: Respuesta de la API
            language: Lenguaje del código
            
        Returns:
            Código extraído
        """
        content = response.get("content", "")
        
        # Buscar bloques de código con el lenguaje específico
        import re
        code_blocks = re.findall(r'```(?:' + language + r'|)\n(.*?)\n```', content, re.DOTALL)
        
        if code_blocks:
            # Devolver el primer bloque de código encontrado
            return code_blocks[0]
        
        # Si no hay bloques de código marcados, intentar encontrar el código por otros medios
        # Por ahora, devolvemos el contenido completo si no se encontraron bloques específicos
        return content
    
    def _extract_issues_from_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraer problemas detectados de la respuesta de la API.
        
        Args:
            response: Respuesta de la API
            
        Returns:
            Lista de problemas detectados
        """
        content = response.get("content", "")
        issues = []
        
        # Patrones para extraer información de problemas
        import re
        issue_pattern = r'(\d+)\.\s+\[([^\]]+)\]:\s+([^\n]+)'
        detail_pattern = r'-\s+([^:]+):\s+([^\n]+)'
        
        # Encontrar todos los problemas
        matches = re.finditer(issue_pattern, content)
        
        for match in matches:
            issue_num = match.group(1)
            issue_type = match.group(2)
            description = match.group(3).strip()
            
            # Buscar detalles relacionados con este problema
            issue_content = content[match.end():]
            end_pos = issue_content.find(f"{int(issue_num)+1}. ")
            if end_pos == -1:
                end_pos = len(issue_content)
            
            issue_details = issue_content[:end_pos]
            
            # Extraer detalles
            location = ""
            severity = ""
            fix = ""
            
            for detail_match in re.finditer(detail_pattern, issue_details):
                detail_type = detail_match.group(1).strip().lower()
                detail_value = detail_match.group(2).strip()
                
                if "location" in detail_type:
                    location = detail_value
                elif "severity" in detail_type:
                    severity = detail_value
                elif "fix" in detail_type:
                    fix = detail_value
            
            # Añadir problema a la lista
            issues.append({
                "type": issue_type,
                "description": description,
                "location": location,
                "severity": severity,
                "fix": fix
            })
        
        return issues
    
    def _extract_refactoring_suggestions(self, response: Dict[str, Any]) -> List[str]:
        """
        Extraer sugerencias de refactorización de la respuesta de la API.
        
        Args:
            response: Respuesta de la API
            
        Returns:
            Lista de sugerencias
        """
        content = response.get("content", "")
        suggestions = []
        
        # Buscar sección de mejoras o sugerencias
        import re
        
        # Patrones comunes para identificar sugerencias
        patterns = [
            r'Key improvements(?:[^\n]*)?:(.*?)(?=\n\n|\n#|\n```|$)',
            r'Improvements(?:[^\n]*)?:(.*?)(?=\n\n|\n#|\n```|$)',
            r'Changes(?:[^\n]*)?:(.*?)(?=\n\n|\n#|\n```|$)',
            r'(?:^|\n)(\d+\.\s+[^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                for match in matches:
                    # Limpiar y dividir en líneas si es una lista
                    if isinstance(match, str) and match.strip():
                        lines = [line.strip() for line in match.strip().split('\n') if line.strip()]
                        for line in lines:
                            # Si es un elemento de lista numerado
                            if re.match(r'^\d+\.\s+', line):
                                suggestions.append(line)
                            # Si es un elemento de lista con viñetas
                            elif line.startswith('- ') or line.startswith('* '):
                                suggestions.append(line)
                            # Si es texto normal
                            elif line and not line.startswith('#'):
                                suggestions.append(line)
        
        # Si no se encontraron sugerencias con los patrones anteriores
        if not suggestions:
            # Intentar extraer párrafos que parecen sugerencias
            potential_suggestions = [p for p in content.split('\n\n') 
                                     if 'improve' in p.lower() or 'refactor' in p.lower() 
                                     or 'better' in p.lower() or 'optimiz' in p.lower()]
            if potential_suggestions:
                suggestions = potential_suggestions[:3]  # Limitar a 3 sugerencias
        
        return suggestions


def get_advanced_anthropic_client(config: Optional[ConfigManager] = None) -> AdvancedAnthropicClient:
    """
    Obtener una instancia del cliente avanzado de Anthropic.
    
    Args:
        config: Configuración opcional
    
    Returns:
        Instancia de AdvancedAnthropicClient
    """
    return AdvancedAnthropicClient(config=config)
