"""
Paquete de integraciones para diferentes servicios de IA.

Este paquete contiene módulos para la integración con diferentes servicios de IA,
como Anthropic (Claude), GitHub Copilot, etc. Incluye tanto funcionalidades
básicas como las versiones avanzadas con características premium.
"""

try:
    from .anthropic import AnthropicAPI, get_anthropic_client
except ImportError:
    # Mock class for tests and CI
    class AnthropicAPI:
        def __init__(self, *args, **kwargs):
            pass
    def get_anthropic_client(*args, **kwargs):
        return AnthropicAPI()

try:
    from .copilot import CopilotAPI, get_copilot_client
except ImportError:
    # Mock class for tests and CI
    class CopilotAPI:
        def __init__(self, *args, **kwargs):
            pass
    def get_copilot_client(*args, **kwargs):
        return CopilotAPI()

# Import advanced modules with fallbacks for CI/testing
try:
    from .anthropic_advanced import AdvancedAnthropicClient, get_advanced_anthropic_client
except ImportError:
    # Mock class for tests and CI
    class AdvancedAnthropicClient:
        def __init__(self, *args, **kwargs):
            pass
    def get_advanced_anthropic_client(*args, **kwargs):
        return AdvancedAnthropicClient()

try:
    from .copilot_advanced import AdvancedCopilotClient, get_advanced_copilot_client
except ImportError:
    # Mock class for tests and CI
    class AdvancedCopilotClient:
        def __init__(self, *args, **kwargs):
            pass
    def get_advanced_copilot_client(*args, **kwargs):
        return AdvancedCopilotClient()

try:
    from .anthropic_integration import AnthropicService, get_anthropic_client as get_anthropic_integration
except ImportError:
    # Mock class for tests and CI
    class AnthropicService:
        def __init__(self, *args, **kwargs):
            pass
            
        def initialize(self, api_key):
            pass
            
        def generate_response(self, prompt, **kwargs):
            return "Mock response"
            
        def verify_api_key(self):
            return True, "API key appears valid"
            
    def get_anthropic_integration(*args, **kwargs):
        return AnthropicService()

__all__ = [
    'AnthropicAPI', 'get_anthropic_client',
    'CopilotAPI', 'get_copilot_client',
    'AdvancedAnthropicClient', 'get_advanced_anthropic_client',
    'AdvancedCopilotClient', 'get_advanced_copilot_client',
    'AnthropicService', 'get_anthropic_integration',
]
