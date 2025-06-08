"""
Unified AI client for ProjectPrompt.
Provides a single interface for different AI providers.
"""

import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """Base class for AI clients."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using AI provider."""
        pass
    
    @abstractmethod
    def analyze_project(self, project_context: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze project using AI provider."""
        pass
    
    @abstractmethod
    def generate_suggestions(self, project_context: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate improvement suggestions."""
        pass


class AIClient:
    """Unified AI client that automatically selects the best available provider."""
    
    def __init__(self, config=None):
        """Initialize AI client with configuration.
        
        Args:
            config: Configuration object with AI settings
        """
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on configuration."""
        provider = None
        
        if self.config:
            provider = getattr(self.config, 'ai_provider', 'auto')
        else:
            provider = os.getenv('PROJECT_PROMPT_AI_PROVIDER', 'auto')
        
        if provider == 'auto':
            provider = self._auto_detect_provider()
        
        if provider == 'anthropic':
            from .anthropic import AnthropicClient
            api_key = None
            if self.config:
                api_key = getattr(self.config, 'anthropic_api_key', None)
            self.client = AnthropicClient(api_key)
        elif provider == 'openai':
            from .openai import OpenAIClient
            api_key = None
            if self.config:
                api_key = getattr(self.config, 'openai_api_key', None)
            self.client = OpenAIClient(api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def _auto_detect_provider(self) -> str:
        """Auto-detect the best available AI provider."""
        # Check for API keys in order of preference
        if os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic'
        elif os.getenv('OPENAI_API_KEY'):
            return 'openai'
        else:
            # Default to anthropic (will show configuration error)
            return 'anthropic'
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using the configured AI provider."""
        if not self.client:
            raise RuntimeError("AI client not properly initialized")
        
        return self.client.generate_response(prompt, **kwargs)
    
    def analyze_project(self, project_context: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze project using the configured AI provider."""
        if not self.client:
            raise RuntimeError("AI client not properly initialized")
        
        return self.client.analyze_project(project_context, analysis_type)
    
    def generate_suggestions(self, project_context: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate improvement suggestions using the configured AI provider."""
        if not self.client:
            raise RuntimeError("AI client not properly initialized")
        
        return self.client.generate_suggestions(project_context, focus_areas)
    
    def is_configured(self) -> bool:
        """Check if the AI client is properly configured."""
        return self.client is not None
