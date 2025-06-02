#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Optimizador de prompts para APIs de IA.

Este módulo contiene funciones y clases para optimizar prompts antes de enviarlos
a las diferentes APIs de IA soportadas, mejorando la calidad de las respuestas.
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple
import json

from src.utils.logger import get_logger
from src.utils.config import ConfigManager
# Premium features now available for all users

logger = get_logger()

class PromptOptimizer:
    """
    Optimizador de prompts para diferentes modelos de IA.
    
    Aplica técnicas de optimización específicas para cada proveedor y tipo de tarea,
    mejorando así la calidad de las respuestas generadas.
    """
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar el optimizador de prompts.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or ConfigManager()
        # Premium features now available for all users
        self.is_premium = True
        
        # Carga de plantillas y técnicas de optimización desde configuración
        self._load_optimization_templates()
        
    def _load_optimization_templates(self) -> None:
        """Cargar plantillas de optimización específicas para cada modelo."""
        # Plantillas básicas por defecto (se ampliarían en la implementación real)
        self.templates = {
            "anthropic": {
                "code_generation": {
                    "prefix": "I need to generate high-quality, well-structured code. Please provide a solution for the following task:\n",
                    "suffix": "\nThe code should be clean, efficient, and follow best practices. Include comments for complex sections."
                },
                "error_detection": {
                    "prefix": "The following code might contain bugs or inefficiencies. Please analyze it and identify any problems:\n",
                    "suffix": "\nFor each issue you find, explain why it's problematic and suggest a fix."
                },
                "refactoring": {
                    "prefix": "I need to refactor the following code to improve its quality. Please analyze it and suggest improvements:\n",
                    "suffix": "\nFocus on improving readability, maintainability, and efficiency while preserving functionality."
                }
            },
            "copilot": {
                "code_generation": {
                    "prefix": "// Task: Create a well-structured implementation for the following:\n",
                    "suffix": "\n// Requirements: Code should be clean, readable, and efficient."
                },
                "error_detection": {
                    "prefix": "// The following code needs to be reviewed for bugs and inefficiencies:\n",
                    "suffix": "\n// Please identify issues and provide fixes."
                },
                "refactoring": {
                    "prefix": "// This code needs to be refactored. Please improve it:\n",
                    "suffix": "\n// Goal: Improve readability and efficiency."
                }
            }
        }
        
        # Técnicas de optimización
        self.techniques = {
            "basic": ["format_code_blocks", "add_task_context"],
            "premium": ["decompose_complex_task", "add_examples", "specify_output_format"]
        }
        
    def optimize(self, 
               prompt: str, 
               provider: str, 
               task_type: str, 
               context: Optional[Dict[str, Any]] = None) -> str:
        """
        Optimizar un prompt para un proveedor y tipo de tarea específicos.
        
        Args:
            prompt: El prompt original a optimizar
            provider: El proveedor de IA ('anthropic' o 'copilot')
            task_type: Tipo de tarea (code_generation, error_detection, etc.)
            context: Contexto adicional para la optimización
            
        Returns:
            El prompt optimizado
        """
        logger.info(f"Optimizando prompt para {provider}, tarea {task_type}")
        
        # Contexto por defecto si no se proporciona
        context = context or {}
        
        # Aplicar técnicas básicas
        optimized_prompt = prompt
        
        # Obtener template específico para el proveedor y tipo de tarea
        template = self.templates.get(provider, {}).get(task_type, {})
        prefix = template.get("prefix", "")
        suffix = template.get("suffix", "")
        
        # Aplicar plantilla básica
        optimized_prompt = f"{prefix}{optimized_prompt}{suffix}"
        
        # Aplicar técnicas básicas de optimización
        for technique in self.techniques["basic"]:
            technique_method = getattr(self, f"_apply_{technique}", None)
            if technique_method and callable(technique_method):
                optimized_prompt = technique_method(optimized_prompt, context)
        
        # Aplicar técnicas premium si el usuario tiene suscripción
        if self.is_premium:
            logger.info("Aplicando optimizaciones premium")
            for technique in self.techniques["premium"]:
                technique_method = getattr(self, f"_apply_{technique}", None)
                if technique_method and callable(technique_method):
                    optimized_prompt = technique_method(optimized_prompt, context)
        
        return optimized_prompt
    
    def _apply_format_code_blocks(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Asegurar que los bloques de código estén correctamente formateados.
        
        Args:
            prompt: El prompt a optimizar
            context: Contexto adicional
            
        Returns:
            Prompt con bloques de código formateados
        """
        # Detectar si hay código que no está encerrado en bloques de código
        code_pattern = r"((?:^|\n)(?:\s*?(?:def|class|import|from|if|for|while|with|try|return)\s+.*?(?:\n|$)){2,})"
        
        # Si encuentra código que no está en un bloque de código markdown, lo encierra
        def replace_with_code_block(match):
            code = match.group(1)
            if "```" not in code:
                return f"\n```python\n{code}\n```\n"
            return code
            
        return re.sub(code_pattern, replace_with_code_block, prompt)
    
    def _apply_add_task_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Añadir contexto relevante a la tarea.
        
        Args:
            prompt: El prompt a optimizar
            context: Contexto adicional
            
        Returns:
            Prompt con contexto añadido
        """
        # Añadir información de contexto si está disponible
        if context.get("project_context"):
            return f"Project context: {context['project_context']}\n\n{prompt}"
        return prompt
    
    def _apply_decompose_complex_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Descomponer tareas complejas en pasos más sencillos (premium).
        
        Args:
            prompt: El prompt a optimizar
            context: Contexto adicional
            
        Returns:
            Prompt con la tarea descompuesta
        """
        # Solo añadir descomposición si el prompt parece complejo
        is_complex = len(prompt.split()) > 100 or prompt.count("\n") > 5
        
        if is_complex:
            steps = [
                "1. Understand the requirements completely",
                "2. Identify core components and dependencies",
                "3. Plan the implementation approach",
                "4. Develop the solution step by step",
                "5. Review and refine the implementation"
            ]
            
            steps_text = "\n".join(steps)
            return f"{prompt}\n\nPlease approach this task systematically:\n{steps_text}"
        
        return prompt
    
    def _apply_add_examples(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Añadir ejemplos ilustrativos para mejorar la comprensión (premium).
        
        Args:
            prompt: El prompt a optimizar
            context: Contexto adicional
            
        Returns:
            Prompt con ejemplos añadidos
        """
        # Añadir ejemplos si están disponibles en el contexto
        if examples := context.get("examples"):
            examples_text = "\n\n".join([f"Example {i+1}:\n```\n{example}\n```" 
                                       for i, example in enumerate(examples)])
            return f"{prompt}\n\nHere are some examples for reference:\n{examples_text}"
        
        return prompt
    
    def _apply_specify_output_format(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Especificar formato de salida deseado (premium).
        
        Args:
            prompt: El prompt a optimizar
            context: Contexto adicional
            
        Returns:
            Prompt con formato de salida especificado
        """
        if output_format := context.get("output_format"):
            return f"{prompt}\n\nPlease ensure your response follows this format:\n{output_format}"
        
        return prompt


def get_prompt_optimizer(config: Optional[ConfigManager] = None) -> PromptOptimizer:
    """
    Obtener una instancia del optimizador de prompts.
    
    Args:
        config: Configuración opcional
    
    Returns:
        Instancia de PromptOptimizer
    """
    return PromptOptimizer(config=config)
