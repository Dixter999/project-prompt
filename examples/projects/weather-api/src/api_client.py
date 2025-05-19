#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather API Client

This module provides a client for retrieving weather data from the
OpenWeather API service.
"""

import requests
from datetime import datetime
import time
import logging
from . import config
from .utils import format_temperature, convert_unix_timestamp, store_in_cache, get_from_cache

logger = logging.getLogger("weather-api.client")

class WeatherAPIClient:
    """
    Client for interacting with the OpenWeather API.
    Provides methods for retrieving current weather and forecasts.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the API client.
        
        Args:
            api_key (str, optional): API key for OpenWeather API. 
                     If not provided, uses the key from config.
        """
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        self.base_url = config.API_BASE_URL
        self.timeout = config.REQUEST_TIMEOUT
        self.enable_cache = config.ENABLE_CACHE
        
        if not self.api_key:
            logger.error("API key is required")
            raise ValueError("API key is required")
        
        logger.info("Weather API client initialized")
    
    def _make_request(self, endpoint, params):
        """
        Make an HTTP request to the weather API.
        
        Args:
            endpoint (str): API endpoint to call
            params (dict): Query parameters for the request
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            ConnectionError: If the request fails
            ValueError: If the API returns an error
        """
        # Add API key to parameters
        params["appid"] = self.api_key
        
        # Check cache if enabled
        if self.enable_cache:
            cache_key = f"{endpoint}_{str(params)}"
            cached_data = get_from_cache(cache_key)
            if cached_data:
                logger.debug("Returning cached data")
                return cached_data
        
        # Build the URL
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = requests.get(url, params=params, timeout=self.timeout)
            
            # Raise exception for error status codes
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result if enabled
            if self.enable_cache:
                store_in_cache(cache_key, data, config.CACHE_EXPIRY)
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise ConnectionError(f"Failed to connect to weather API: {e}")
    
    def get_current_weather(self, city, units="metric"):
        """
        Get current weather for a city.
        
        Args:
            city (str): City name (e.g., "London,UK")
            units (str): Units for temperature (metric, imperial, standard)
            
        Returns:
            dict: Weather data for the specified city
        """
        logger.info(f"Getting current weather for {city}")
        
        params = {
            "q": city,
            "units": units
        }
        
        data = self._make_request("weather", params)
        
        # Process and enhance the data
        if "main" in data and "temp" in data["main"]:
            data["main"]["formatted_temp"] = format_temperature(
                data["main"]["temp"], units
            )
            
        if "dt" in data:
            data["formatted_time"] = convert_unix_timestamp(data["dt"])
            
        return data
    
    def get_forecast(self, city, days=5, units="metric"):
        """
        Get weather forecast for a city.
        
        Args:
            city (str): City name (e.g., "London,UK")
            days (int): Number of days for forecast (max 5)
            units (str): Units for temperature (metric, imperial, standard)
            
        Returns:
            dict: Forecast data for the specified city
        """
        logger.info(f"Getting {days}-day forecast for {city}")
        
        # Ensure days is within valid range
        days = max(1, min(days, 5))
        
        params = {
            "q": city,
            "units": units,
            "cnt": days * 8  # API returns data in 3-hour increments
        }
        
        data = self._make_request("forecast", params)
        
        # Process and enhance the data
        if "list" in data:
            for item in data["list"]:
                if "main" in item and "temp" in item["main"]:
                    item["main"]["formatted_temp"] = format_temperature(
                        item["main"]["temp"], units
                    )
                
                if "dt" in item:
                    item["formatted_time"] = convert_unix_timestamp(item["dt"])
        
        return data
