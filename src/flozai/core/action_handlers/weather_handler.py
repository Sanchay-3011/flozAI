"""
Weather Action Handler
Fetches current weather data from Open-Meteo (No API key required).
"""
import requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

class WeatherHandler:
    """Handles weather-related actions."""

    # Simple coordinate mapping for common locations
    LOCATION_MAPPING = {
        "punjab": {"lat": 31.1471, "lon": 75.3412},
        "delhi": {"lat": 28.6139, "lon": 77.2090},
        "mumbai": {"lat": 19.0760, "lon": 72.8777},
        "london": {"lat": 51.5074, "lon": -0.1278},
        "new york": {"lat": 40.7128, "lon": -74.0060},
        "san francisco": {"lat": 37.7749, "lon": -122.4194},
    }

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        if action == "get_weather":
            return self._get_weather(params)
        else:
            raise ValueError(f"Unknown weather action: {action}")

    def _get_weather(self, params: dict) -> dict:
        location = params.get("location", "Punjab").lower()
        
        # Try to find coordinates
        coords = self.LOCATION_MAPPING.get(location)
        
        if not coords:
            # Fallback to Punjab if location not found in mapping
            logger.warning(f"Location '{location}' not in mapping, falling back to Punjab.")
            coords = self.LOCATION_MAPPING["punjab"]
            location = "Punjab (Default)"

        lat, lon = coords["lat"], coords["lon"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current_weather", {})
            temp = current.get("temperature")
            windspeed = current.get("windspeed")
            
            return {
                "location": location.capitalize(),
                "temperature": f"{temp}°C",
                "windspeed": f"{windspeed} km/h",
                "status": "success",
                "raw_data": current
            }
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return {
                "location": location.capitalize(),
                "status": "error",
                "error": str(e)
            }
