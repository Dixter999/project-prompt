"""AI service manager for handling multiple AI providers.

This module provides a unified interface to interact with different AI services
like OpenAI and Anthropic, allowing easy switching between them.
"""

from typing import Optional, Dict, Any, Type, Union
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AIService(ABC):
    """Abstract base class for AI services."""
    
    @abstractmethod
    def initialize(self, api_key: str) -> None:
        """Initialize the AI service with an API key.
        
        Args:
            api_key: The API key for the service
        """
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response to the given prompt.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the API call
            
        Returns:
            The generated response text
        """
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the service is properly configured."""
        pass


class AIManager:
    """Manager for handling multiple AI services."""
    
    def __init__(self):
        """Initialize the AI manager with configured services."""
        self.services: Dict[str, AIService] = {}
        self._setup_services()
    
    def _setup_services(self) -> None:
        """Set up the available AI services."""
        from src.integrations.openai_integration import OpenAIService
        from src.integrations.anthropic import AnthropicAPI
        
        # Initialize OpenAI service
        openai_key = self._get_api_key("openai")
        if openai_key:
            self.services["openai"] = OpenAIService()
            self.services["openai"].initialize(openai_key)
        
        # Initialize Anthropic service
        anthropic_key = self._get_api_key("anthropic")
        if anthropic_key:
            self.services["anthropic"] = AnthropicAPI()
            self.services["anthropic"].initialize(anthropic_key)
    
    def _get_api_key(self, service: str) -> Optional[str]:
        """Get the API key for the specified service.
        
        Args:
            service: The service name (e.g., 'openai', 'anthropic')
            
        Returns:
            The API key if found, None otherwise
        """
        from src.utils.config import get_config
        
        try:
            config = get_config()
            return config.get("api_keys", {}).get(service)
        except Exception as e:
            logger.warning(f"Failed to get API key for {service}: {e}")
            return None
    
    def get_service(self, service_name: str) -> Optional[AIService]:
        """Get an AI service by name.
        
        Args:
            service_name: The name of the service to get
            
        Returns:
            The service instance if found, None otherwise
        """
        return self.services.get(service_name.lower())
    
    def generate_ai_response(
        self, 
        prompt: str, 
        service: str = "openai", 
        **kwargs
    ) -> Optional[str]:
        """Generate a response using the specified AI service.
        
        Args:
            prompt: The input prompt
            service: The name of the AI service to use
            **kwargs: Additional parameters for the API call
            
        Returns:
            The generated response, or None if the service is not available
        """
        ai_service = self.get_service(service)
        if not ai_service:
            logger.error(f"AI service '{service}' is not available")
            return None
            
        if not ai_service.is_configured:
            logger.error(f"AI service '{service}' is not properly configured")
            return None
            
        try:
            return ai_service.generate_response(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Error generating response from {service}: {e}")
            return None


def get_ai_manager() -> AIManager:
    """Get a configured instance of the AI manager.
    
    Returns:
        An initialized AIManager instance
    """
    return AIManager()
