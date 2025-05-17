#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Versión simplificada del generador de prompts para implementación.
Esta versión se crea para solucionar problemas de sintaxis con f-strings.
"""

from src.utils.logger import get_logger

# Configurar logger
logger = get_logger()

class ImplementationPromptGenerator:
    """Generador simplificado de prompts para implementación."""
    
    def __init__(self, is_premium=False):
        """Inicializar generador."""
        self.is_premium = is_premium
    
    def generate_implementation_prompt(self, project_path, feature_name):
        """Genera un prompt para implementación (versión simplificada)."""
        return {
            "success": True,
            "prompts": {
                "implementation": f"# Implementación de {feature_name}\nEsta es una versión simplificada.",
                "integration": None,
                "testing": None
            },
            "feature_info": {"name": feature_name},
            "related_files": []
        }


def get_implementation_prompt_generator(is_premium=False):
    """Obtiene una instancia del generador de prompts."""
    return ImplementationPromptGenerator()
