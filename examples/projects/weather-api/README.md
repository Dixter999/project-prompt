# Weather API Client

A simple Python application that connects to a weather API, retrieves data, and displays it to the user.

## Features

- Connect to OpenWeather API
- Retrieve current weather data by city name
- Retrieve weather forecast data
- Display weather information in a formatted way
- Command-line interface for easy interaction

## Installation

```bash
# Clone the repository
git clone https://github.com/example/weather-api-client.git
cd weather-api-client

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API key
```

## Usage

```bash
# Get current weather for a city
python -m src.cli weather current "New York"

# Get 5-day forecast for a city
python -m src.cli weather forecast "London" --days 5

# Get weather with temperature unit
python -m src.cli weather current "Tokyo" --unit celsius
```

## Configuration

Create a `.env` file with the following:

```
OPENWEATHER_API_KEY=your_api_key_here
```

You can get an API key by signing up at [OpenWeatherMap](https://openweathermap.org/api).

## Project Structure

- `src/api_client.py`: Core API client for connecting to the weather service
- `src/cli.py`: Command-line interface for the application
- `src/utils.py`: Utility functions for data processing and formatting
- `src/config.py`: Configuration handling (environment variables, etc.)

## Development

```bash
# Run tests
pytest tests/

# Run linting
flake8 src/
```

## License

MIT
