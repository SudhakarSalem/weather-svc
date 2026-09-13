import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

class WeatherFetcher:
    """Fetch weather data from multiple sources"""

    def __init__(self):
        self.openweather_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.api_ninjas_key = os.getenv("API_NINJAS_API_KEY")
        self.openweather_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.api_ninjas_url = "https://api.api-ninjas.com/v1/weather"

    def get_coordinates(self, city: str) -> Optional[Dict]:
        """Get latitude and longitude for a city using OpenWeatherMap's geocoder"""
        try:
            geo_url = "https://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": city,
                "limit": 1,
                "appid": self.openweather_key
            }
            response = requests.get(geo_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data:
                return {
                    "city": data[0].get("name"),
                    "country": data[0].get("country"),
                    "lat": data[0].get("lat"),
                    "lon": data[0].get("lon")
                }
            print(f"Geocoding: no results found for '{city}'")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching coordinates: {e} | body: {e.response.text[:300]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def get_openweather_forecast(self, city: str, coords: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch tomorrow's weather from OpenWeatherMap"""
        try:
            coords = coords or self.get_coordinates(city)
            if not coords:
                return None

            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.openweather_key,
                "units": "metric"
            }

            response = requests.get(self.openweather_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Get tomorrow's forecast entries
            tomorrow_data = {
                "source": "OpenWeatherMap",
                "city": coords["city"],
                "country": coords["country"],
                "forecasts": []
            }

            tomorrow_date = (datetime.now() + timedelta(days=1)).date()

            for item in data.get("list", []):
                forecast_date = datetime.fromtimestamp(item["dt"]).date()

                if forecast_date == tomorrow_date:
                    tomorrow_data["forecasts"].append({
                        "time": datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d %H:%M"),
                        "temperature": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "humidity": item["main"]["humidity"],
                        "pressure": item["main"]["pressure"],
                        "description": item["weather"][0]["description"],
                        "wind_speed": item["wind"]["speed"]
                    })

            return tomorrow_data if tomorrow_data["forecasts"] else None

        except requests.exceptions.HTTPError as e:
            print(f"Error fetching OpenWeatherMap data: {e} | body: {e.response.text[:300]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching OpenWeatherMap data: {e}")
            return None

    def get_api_ninjas_weather(self, city: str, coords: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch current weather from API Ninjas.

        Uses lat/lon (from OpenWeatherMap geocoding) instead of the raw city
        name whenever available. API Ninjas' city-name matching is far less
        forgiving than lat/lon lookups and frequently 400s on valid city
        names (accented characters, less common cities, multi-word names,
        etc.), so preferring coordinates avoids most of those failures.
        """
        try:
            headers = {"X-Api-Key": self.api_ninjas_key}

            if coords and coords.get("lat") is not None and coords.get("lon") is not None:
                params = {"lat": coords["lat"], "lon": coords["lon"]}
            else:
                params = {"city": city}

            response = requests.get(self.api_ninjas_url, params=params, headers=headers, timeout=10)

            if response.status_code == 400:
                # Fall back to city-name lookup if a coordinate lookup was rejected,
                # or surface the real error body if city-name lookup itself failed.
                print(f"API Ninjas 400 for params={params}: {response.text[:300]}")
                if "lat" in params:
                    params = {"city": city}
                    response = requests.get(self.api_ninjas_url, params=params, headers=headers, timeout=10)

            response.raise_for_status()
            data = response.json()

            sunrise = data.get("sunrise")
            sunset = data.get("sunset")

            return {
                "source": "API Ninjas",
                "city": (coords or {}).get("city", city),
                "country": (coords or {}).get("country"),
                "temperature": data.get("temp"),
                "feels_like": data.get("feels_like"),
                "min_temp": data.get("min_temp"),
                "max_temp": data.get("max_temp"),
                "humidity": data.get("humidity"),
                "wind_speed": data.get("wind_speed"),
                "wind_direction": data.get("wind_degrees"),
                "cloudiness": data.get("cloud_pct"),
                "sunrise": datetime.fromtimestamp(sunrise).strftime("%H:%M") if sunrise else None,
                "sunset": datetime.fromtimestamp(sunset).strftime("%H:%M") if sunset else None,
            }

        except requests.exceptions.HTTPError as e:
            print(f"Error fetching API Ninjas data: {e} | body: {e.response.text[:300]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching API Ninjas data: {e}")
            return None

    def get_combined_weather(self, city: str) -> Dict:
        """Get weather data from both sources, sharing one geocoding lookup"""
        coords = self.get_coordinates(city)
        return {
            "openweather": self.get_openweather_forecast(city, coords=coords),
            "api_ninjas": self.get_api_ninjas_weather(city, coords=coords)
        }
