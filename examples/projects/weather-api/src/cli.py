#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Line Interface for Weather API Client

This module provides a CLI for interacting with the Weather API client.
"""

import click
import sys
import logging
from tabulate import tabulate
from colorama import Fore, Style, init

from . import config
from .api_client import WeatherAPIClient
from .utils import display_weather_data

# Initialize colorama for colored terminal output
init()

logger = logging.getLogger("weather-api.cli")

@click.group()
def cli():
    """
    Weather API Client - Command Line Interface
    
    A tool for retrieving and displaying weather information.
    """
    pass

@cli.group()
def weather():
    """Commands for retrieving weather information."""
    pass

@weather.command("current")
@click.argument("city")
@click.option("--unit", "-u", default="metric", 
              type=click.Choice(["metric", "imperial", "standard"]),
              help="Temperature unit (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
@click.option("--format", "-f", "output_format", default="table",
              type=click.Choice(["table", "text"]),
              help="Output format")
def get_current_weather(city, unit, output_format):
    """
    Get current weather for a city.
    
    CITY: Name of the city (e.g., "London" or "New York,US")
    """
    try:
        # Validate config
        config.validate_config()
        
        # Initialize client
        client = WeatherAPIClient()
        
        # Get weather data
        weather_data = client.get_current_weather(city, units=unit)
        
        # Display results
        if output_format == "table":
            output = display_weather_data(weather_data, format_type="table")
            click.echo("\n" + output)
        else:
            output = display_weather_data(weather_data, format_type="text")
            click.echo("\n" + Fore.CYAN + output + Style.RESET_ALL)
            
    except ValueError as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(Fore.RED + f"Connection error: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(Fore.RED + f"An unexpected error occurred: {e}" + Style.RESET_ALL)
        sys.exit(1)

@weather.command("forecast")
@click.argument("city")
@click.option("--days", "-d", default=5, type=click.IntRange(1, 5),
              help="Number of days for forecast (1-5)")
@click.option("--unit", "-u", default="metric", 
              type=click.Choice(["metric", "imperial", "standard"]),
              help="Temperature unit (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
@click.option("--format", "-f", "output_format", default="table",
              type=click.Choice(["table", "text"]),
              help="Output format")
def get_forecast(city, days, unit, output_format):
    """
    Get weather forecast for a city.
    
    CITY: Name of the city (e.g., "London" or "New York,US")
    """
    try:
        # Validate config
        config.validate_config()
        
        # Initialize client
        client = WeatherAPIClient()
        
        # Get forecast data
        forecast_data = client.get_forecast(city, days=days, units=unit)
        
        if "list" not in forecast_data or not forecast_data["list"]:
            click.echo(Fore.RED + "No forecast data available" + Style.RESET_ALL)
            return
        
        # Extract city information
        city_name = forecast_data.get("city", {}).get("name", city)
        country = forecast_data.get("city", {}).get("country", "")
        
        click.echo(f"\n{Fore.GREEN}Weather Forecast for {city_name}, {country}{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}{'-' * 50}{Style.RESET_ALL}")
        
        # Group forecast by day
        forecasts_by_day = {}
        
        for item in forecast_data["list"]:
            # Get date from timestamp
            date_str = item["formatted_time"].split()[0]
            
            if date_str not in forecasts_by_day:
                forecasts_by_day[date_str] = []
                
            forecasts_by_day[date_str].append(item)
        
        # Display forecast for each day
        for date_str, items in forecasts_by_day.items():
            click.echo(f"\n{Fore.YELLOW}Date: {date_str}{Style.RESET_ALL}")
            
            if output_format == "table":
                table_data = []
                
                for item in items:
                    time = item["formatted_time"].split()[1]
                    temp = item["main"]["formatted_temp"]
                    description = item["weather"][0]["description"].capitalize()
                    humidity = f"{item['main']['humidity']}%"
                    wind = f"{item['wind']['speed']} m/s"
                    
                    table_data.append([time, temp, description, humidity, wind])
                
                headers = ["Time", "Temp", "Conditions", "Humidity", "Wind"]
                click.echo(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            else:
                for item in items:
                    time = item["formatted_time"].split()[1]
                    temp = item["main"]["formatted_temp"]
                    description = item["weather"][0]["description"].capitalize()
                    
                    click.echo(
                        f"{Fore.CYAN}{time}{Style.RESET_ALL}: "
                        f"{temp}, {description}"
                    )
    
    except ValueError as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(Fore.RED + f"Connection error: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(Fore.RED + f"An unexpected error occurred: {e}" + Style.RESET_ALL)
        sys.exit(1)

@cli.command("version")
def show_version():
    """Show version information."""
    from importlib.metadata import version, PackageNotFoundError
    
    try:
        ver = version("weather-api-client")
        click.echo(f"Weather API Client v{ver}")
    except PackageNotFoundError:
        click.echo("Weather API Client v0.1.0 (development)")

if __name__ == "__main__":
    cli()
