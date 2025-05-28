"""
OpenAI Integration Module.

This module provides integration with OpenAI's API for GPT models.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIAPI:
    """Client for OpenAI API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI API client.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return self.client is not None and self.api_key is not None
    
    def generate_completion(self, 
                          prompt: str, 
                          model: str = "gpt-3.5-turbo",
                          max_tokens: int = 1000,
                          temperature: float = 0.7) -> Optional[str]:
        """
        Generate completion using OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            model: Model to use for completion
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated completion text or None if error
        """
        if not self.is_configured():
            logger.error("OpenAI client not configured")
            return None
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def validate_api_key(self) -> Dict[str, Any]:
        """
        Validate the OpenAI API key.
        
        Returns:
            Dict with validation results
        """
        if not self.api_key:
            return {
                "valid": False,
                "error": "No API key provided"
            }
            
        try:
            # Try a simple request to validate the key
            response = self.client.models.list()
            
            return {
                "valid": True,
                "models_available": len(response.data),
                "message": "OpenAI API key is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


def get_openai_client(api_key: Optional[str] = None) -> OpenAIAPI:
    """
    Get configured OpenAI client instance.
    
    Args:
        api_key: Optional API key. If not provided, will use environment variable.
        
    Returns:
        OpenAI client instance
    """
    return OpenAIAPI(api_key=api_key)
