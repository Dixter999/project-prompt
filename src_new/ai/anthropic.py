#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integración específica con Anthropic Claude simplificada.
"""

import os
from typing import Dict, Any, Optional


def create_anthropic_client(api_key: Optional[str] = None):
    """
    Crear cliente de Anthropic simplificado.
    
    Args:
        api_key: Clave API opcional
        
    Returns:
        Cliente configurado
    """
    key = api_key or os.getenv('ANTHROPIC_API_KEY')
    
    if not key:
        raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
    
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except ImportError:
        raise ImportError("Librería anthropic no instalada. Ejecute: pip install anthropic")


def generate_code_analysis(client, code: str, language: str = "python") -> Dict[str, Any]:
    """
    Generar análisis de código usando Claude.
    
    Args:
        client: Cliente de Anthropic
        code: Código a analizar
        language: Lenguaje del código
        
    Returns:
        Análisis del código
    """
    prompt = f"""
Analiza el siguiente código {language} y proporciona:

1. Resumen de funcionalidad
2. Posibles mejoras
3. Problemas de calidad identificados
4. Sugerencias de refactorización

CÓDIGO:
```{language}
{code}
```

Proporciona un análisis conciso y práctico.
"""
    
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'success': True,
            'analysis': response.content[0].text
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
