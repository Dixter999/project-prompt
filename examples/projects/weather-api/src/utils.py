#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility Functions for Weather API Client

This module contains utility functions for data processing,
formatting, and caching used by the Weather API client.
"""

import json
import os
import time
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger("weather-api.utils")

# Cache directory
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".weather-api", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def format_temperature(temp, units="metric"):
    """
    Format temperature with appropriate unit.
    
    Args:
        temp (float): Temperature value
        units (str): Units system (metric, imperial, standard)
        
    Returns:
        str: Formatted temperature string
    """
    if units == "metric":
        return f"{temp:.1f}°C"
    elif units == "imperial":
        return f"{temp:.1f}°F"
    else:  # standard (Kelvin)
        return f"{temp:.1f}K"

def convert_unix_timestamp(timestamp):
    """
    Convert Unix timestamp to formatted datetime string.
    
    Args:
        timestamp (int): Unix timestamp
        
    Returns:
        str: Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def store_in_cache(key, data, expiry=1800):
    """
    Store data in cache.
    
    Args:
        key (str): Cache key
        data (dict): Data to cache
        expiry (int): Cache expiry time in seconds
    """
    try:
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        cache_file = os.path.join(CACHE_DIR, f"{safe_key}.json")
        
        # Prepare data with expiry
        cache_data = {
            "data": data,
            "expires_at": time.time() + expiry
        }
        
        # Write to cache file
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
            
        logger.debug(f"Data cached with key: {key}")
    except Exception as e:
        logger.warning(f"Failed to cache data: {e}")

def get_from_cache(key):
    """
    Get data from cache if it exists and is not expired.
    
    Args:
        key (str): Cache key
        
    Returns:
        dict or None: Cached data or None if not found or expired
    """
    try:
        # Create safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        cache_file = os.path.join(CACHE_DIR, f"{safe_key}.json")
        
        # Check if cache file exists
        if not os.path.exists(cache_file):
            return None
        
        # Read from cache file
        with open(cache_file, "r") as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        if time.time() > cache_data.get("expires_at", 0):
            logger.debug(f"Cache expired for key: {key}")
            os.remove(cache_file)
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return cache_data.get("data")
    except Exception as e:
        logger.warning(f"Failed to retrieve from cache: {e}")
        return None

def display_weather_data(data, format_type="table"):
    """
    Format weather data for display.
    
    Args:
        data (dict): Weather data
        format_type (str): Output format (table, text)
        
    Returns:
        str: Formatted weather data
    """
    if not data:
        return "No weather data available"
    
    # Extract main information
    location = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    temp = data.get("main", {}).get("formatted_temp", "N/A")
    description = "N/A"
    
    if "weather" in data and len(data["weather"]) > 0:
        description = data["weather"][0].get("description", "N/A").capitalize()
    
    humidity = data.get("main", {}).get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    
    # Format output based on requested type
    if format_type == "table":
        from tabulate import tabulate
        
        table_data = [
            ["Location", f"{location}, {country}"],
            ["Temperature", temp],
            ["Conditions", description],
            ["Humidity", f"{humidity}%"],
            ["Wind Speed", f"{wind_speed} m/s"]
        ]
        
        return tabulate(table_data, tablefmt="fancy_grid")
    else:
        # Simple text format
        return (
            f"Weather for {location}, {country}:\n"
            f"Temperature: {temp}\n"
            f"Conditions: {description}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )
