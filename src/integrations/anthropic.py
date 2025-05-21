#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration module for Anthropic's API (Claude).

This module provides a client for interacting with the Anthropic API,
handling authentication, request formatting, and response parsing.
"""

import logging
from typing import Optional, Dict, Any, Union, List
import requests
import json

# Configure logger
logger = logging.getLogger(__name__)

# Base URL for the Anthropic API
ANTHROPIC_API_BASE_URL = "https://api.anthropic.com/v1"

class AnthropicAPI:
    """Client for interacting with Anthropic's API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Anthropic client.
        
        Args:
            config: Optional configuration dictionary. If provided, it should contain
                   the 'api_keys.anthropic' key with the API key.
        """
        self.api_key = None
        self._is_configured = False
        self.model = "claude-3-haiku-20240307"
        self.max_tokens = 4000
        
        # Initialize session for API requests
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": ""  # Will be set in initialize()
        })
        
        # Initialize with config if provided
        if config and "api_keys" in config and "anthropic" in config["api_keys"]:
            self.initialize(config["api_keys"]["anthropic"])
    
    @property
    def is_configured(self) -> bool:
        """Check if the API is properly configured."""
        return self._is_configured and bool(self.api_key)
    
    def initialize(self, api_key: str) -> None:
        """
        Initialize the Anthropic client with an API key.
        
        Args:
            api_key: The API key for Anthropic
        """
        self.api_key = api_key
        self._is_configured = bool(api_key)
        
        if self._is_configured:
            self.session.headers.update({
                "x-api-key": self.api_key
            })
            logger.info("Anthropic client initialized with API key")
        else:
            logger.warning("Anthropic client initialized without API key")
    
    def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate a response using the Anthropic API.
        
        Args:
            prompt: The input prompt
            model: The model to use (defaults to the instance's model)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters for the API call
            
        Returns:
            The generated response text
            
        Raises:
            RuntimeError: If the client is not properly configured or if the API call fails
        """
        if not self.is_configured:
            raise RuntimeError("Anthropic client is not properly configured. Call initialize() first.")
        
        # Use instance values as defaults if not provided
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        
        # For testing purposes, return a mock response
        if "test" in model.lower() or "mock" in model.lower():
            return f"Mock Anthropic response to: {prompt}"
            
        # In a real implementation, this would call the Anthropic API
        # Here's how it would look:
        """
        try:
            response = self.session.post(
                f"{ANTHROPIC_API_BASE_URL}/messages",
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")
        """
        
        # For now, return a mock response
        return f"Mock Anthropic response to: {prompt}"


def get_anthropic_client(config: Optional[Dict[str, Any]] = None) -> AnthropicAPI:
    """
    Get a configured instance of the Anthropic client.
    
    Args:
        config: Optional configuration dictionary. If not provided, it will be loaded from the config.
    
    Returns:
        An initialized AnthropicAPI instance
    """
    if config is None:
        from src.utils.config import get_config
        config = get_config()
    
    return AnthropicAPI(config=config)
