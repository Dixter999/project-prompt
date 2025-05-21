"""OpenAI integration for ProjectPrompt.

This module provides functionality to interact with OpenAI's API.
"""

import os
from typing import Dict, Any, Optional, List, Union
import openai
from openai import OpenAI

from src.utils.config import Config


class OpenAIService:
    """Service for interacting with OpenAI's API."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the OpenAI service.
        
        Args:
            config: Optional Config instance. If not provided, a new one will be created.
        """
        self.config = config or Config()
        self.client = OpenAI(api_key=self._get_api_key())
    
    def _get_api_key(self) -> str:
        """Get the OpenAI API key from configuration.
        
        Returns:
            The OpenAI API key.
            
        Raises:
            ValueError: If the API key is not configured.
        """
        api_key = self.config.get("api.openai.key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        return api_key
    
    def generate_response(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate a response using the OpenAI API.
        
        Args:
            prompt: The prompt to send to the API.
            model: The model to use for generation.
            max_tokens: Maximum number of tokens to generate.
            temperature: Controls randomness in the response.
            **kwargs: Additional arguments to pass to the API.
            
        Returns:
            The generated response as a string.
            
        Raises:
            Exception: If there's an error calling the API.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    @classmethod
    def is_configured(cls, config: Optional[Config] = None) -> bool:
        """Check if the OpenAI service is properly configured.
        
        Args:
            config: Optional Config instance. If not provided, a new one will be created.
            
        Returns:
            True if the service is properly configured, False otherwise.
        """
        try:
            config = config or Config()
            api_key = config.get("api.openai.key") or os.getenv("OPENAI_API_KEY")
            return bool(api_key)
        except Exception:
            return False
