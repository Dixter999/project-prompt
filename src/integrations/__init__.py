"""
Paquete de integraciones para diferentes servicios de IA.

Este paquete contiene módulos para la integración con diferentes servicios de IA,
como Anthropic (Claude), GitHub Copilot, etc. Incluye tanto funcionalidades
básicas como las versiones avanzadas con características premium.
"""

from .anthropic import AnthropicAPI, get_anthropic_client
from .copilot import CopilotAPI, get_copilot_client
from .anthropic_advanced import AdvancedAnthropicClient, get_advanced_anthropic_client
from .copilot_advanced import AdvancedCopilotClient, get_advanced_copilot_client
from .openai_integration import OpenAIAPI, get_openai_client
from .anthropic_rules_analyzer import AnthropicRulesAnalyzer, get_anthropic_rules_analyzer

__all__ = [
    'AnthropicAPI', 'get_anthropic_client',
    'CopilotAPI', 'get_copilot_client',
    'AdvancedAnthropicClient', 'get_advanced_anthropic_client',
    'AdvancedCopilotClient', 'get_advanced_copilot_client',
    'OpenAIAPI', 'get_openai_client',
    'AnthropicRulesAnalyzer', 'get_anthropic_rules_analyzer',
]
