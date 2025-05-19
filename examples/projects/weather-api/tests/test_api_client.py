#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Weather API Client
"""

import pytest
import json
import os
import responses
from unittest.mock import patch, MagicMock

from src.api_client import WeatherAPIClient
from src import config

# Sample test data
SAMPLE_WEATHER_DATA = {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [
        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
    ],
    "base": "stations",
    "main": {
        "temp": 15.5,
        "feels_like": 14.8,
        "temp_min": 13.9,
        "temp_max": 16.7,
        "pressure": 1023,
        "humidity": 67
    },
    "visibility": 10000,
    "wind": {"speed": 4.63, "deg": 270},
    "clouds": {"all": 0},
    "dt": 1622908800,
    "sys": {
        "type": 2,
        "id": 2019646,
        "country": "GB",
        "sunrise": 1622865580,
        "sunset": 1622924472
    },
    "timezone": 3600,
    "id": 2643743,
    "name": "London",
    "cod": 200
}

@pytest.fixture
def api_client():
    """Fixture to create a WeatherAPIClient with test API key."""
    with patch.object(config, 'OPENWEATHER_API_KEY', 'test_key'):
        client = WeatherAPIClient("test_key")
        client.enable_cache = False  # Disable caching for tests
        yield client

@responses.activate
def test_get_current_weather(api_client):
    """Test getting current weather."""
    # Mock API response
    responses.add(
        responses.GET,
        f"{config.API_BASE_URL}/weather",
        json=SAMPLE_WEATHER_DATA,
        status=200
    )
    
    # Call the method
    result = api_client.get_current_weather("London")
    
    # Verify the result
    assert result is not None
    assert result["name"] == "London"
    assert "formatted_temp" in result["main"]
    assert "formatted_time" in result

@responses.activate
def test_get_forecast(api_client):
    """Test getting forecast data."""
    # Sample forecast data (simplified)
    sample_forecast = {
        "list": [
            {
                "dt": 1622908800,
                "main": {
                    "temp": 15.5,
                    "humidity": 67
                },
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky"
                    }
                ],
                "wind": {"speed": 4.63}
            },
            {
                "dt": 1622919600,
                "main": {
                    "temp": 14.2,
                    "humidity": 72
                },
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky"
                    }
                ],
                "wind": {"speed": 3.9}
            }
        ],
        "city": {
            "name": "London",
            "country": "GB"
        }
    }
    
    # Mock API response
    responses.add(
        responses.GET,
        f"{config.API_BASE_URL}/forecast",
        json=sample_forecast,
        status=200
    )
    
    # Call the method
    result = api_client.get_forecast("London", days=1)
    
    # Verify the result
    assert result is not None
    assert "list" in result
    assert len(result["list"]) > 0
    assert "formatted_temp" in result["list"][0]["main"]
    assert "formatted_time" in result["list"][0]

def test_api_client_initialization():
    """Test API client initialization."""
    # Test with provided key
    client = WeatherAPIClient("provided_key")
    assert client.api_key == "provided_key"
    
    # Test with missing key
    with pytest.raises(ValueError):
        with patch.object(config, 'OPENWEATHER_API_KEY', None):
            WeatherAPIClient()

def test_format_temperature():
    """Test temperature formatting."""
    from src.utils import format_temperature
    
    # Test metric format (Celsius)
    assert format_temperature(20.5, "metric") == "20.5°C"
    
    # Test imperial format (Fahrenheit)
    assert format_temperature(68.9, "imperial") == "68.9°F"
    
    # Test standard format (Kelvin)
    assert format_temperature(293.15, "standard") == "293.2K"
