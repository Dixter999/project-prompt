"""
Paquete de integraciones para diferentes servicios de IA.

Este paquete contiene módulos para la integración con diferentes servicios de IA,
como Anthropic (Claude), GitHub Copilot, etc.
"""

from .anthropic import AnthropicAPI, get_anthropic_client
from .copilot import CopilotAPI, get_copilot_client

__all__ = [
    'AnthropicAPI', 'get_anthropic_client',
    'CopilotAPI', 'get_copilot_client',
]
