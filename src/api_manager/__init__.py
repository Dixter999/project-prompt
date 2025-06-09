"""
API Manager Module - Sistema de Implementación Adaptativa
Provides API-driven intelligent implementation services.

FASE 1 - Pre-procesamiento y Enriquecimiento:
- ContextBuilder: Intelligent project context analysis
- PromptEnricher: Advanced prompt enhancement and optimization  
- AnthropicClient: API client with caching and performance tracking
- RequestOptimizer: Multi-target request optimization

FASE 2 - Gestión Inteligente de Solicitudes:
- ConversationManager: Multi-turn conversation and context tracking
- ResponseProcessor: API response processing and content extraction
- ImplementationCoordinator: Complex workflow coordination and management
"""

from .context_builder import ContextBuilder
from .prompt_enricher import PromptEnricher
from .anthropic_client import AnthropicClient
from .request_optimizer import RequestOptimizer
from .conversation_manager import ConversationManager
from .response_processor import ResponseProcessor
from .implementation_coordinator import ImplementationCoordinator
from .api_diagnostics import APIDiagnostics, run_quick_diagnosis

__all__ = [
    # FASE 1 Components
    'ContextBuilder',
    'PromptEnricher', 
    'AnthropicClient',
    'RequestOptimizer',
    # FASE 2 Components
    'ConversationManager',
    'ResponseProcessor',
    'ImplementationCoordinator',
    # Diagnostics
    'APIDiagnostics',
    'run_quick_diagnosis'
]
