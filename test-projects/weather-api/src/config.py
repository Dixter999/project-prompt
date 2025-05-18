#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather API Client Configuration

This module handles configuration settings for the Weather API client,
including loading environment variables and API keys.
"""

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("weather-api")

# Load environment variables from .env file
load_dotenv()

# API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
API_BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_UNITS = os.getenv("DEFAULT_UNITS", "metric")  # metric, imperial, standard

# Cache configuration
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY", "1800"))  # seconds

# Application settings
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))  # seconds

def validate_config():
    """
    Validate that all required configuration variables are set.
    Raises an exception if any required variable is missing.
    """
    if not OPENWEATHER_API_KEY:
        logger.error("Missing API key - set OPENWEATHER_API_KEY environment variable")
        raise ValueError("API key is required. Set OPENWEATHER_API_KEY in .env file")
    
    logger.info("Configuration validated successfully")
    return True
