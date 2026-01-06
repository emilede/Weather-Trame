"""
OpenWeatherMap API Integration
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "http://api.openweathermap.org/geo/1.0"


def search_cities(query, state="OR", country="US", limit=5):
    """
    Search for cities by name.
    Returns list of {name, state, country, lat, lon} dicts.
    """
    try:
        response = requests.get(
            f"{GEO_URL}/direct",
            params={
                "q": f"{query},{state},{country}",
                "limit": limit,
                "appid": API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data:
            results.append({
                "name": item["name"],
                "state": item.get("state", ""),
                "country": item.get("country", ""),
                "lat": item["lat"],
                "lon": item["lon"],
                "display_name": f"{item['name']}, {item.get('state', '')}"
            })
        return results
    except Exception as e:
        print(f"Error searching cities: {e}")
        return []


def get_icon(icon_code):
    """Convert OpenWeatherMap icon code to MDI icon."""
    icon_map = {
        "01d": "mdi-weather-sunny",
        "01n": "mdi-weather-night",
        "02d": "mdi-weather-partly-cloudy",
        "02n": "mdi-weather-night-partly-cloudy",
        "03d": "mdi-weather-cloudy",
        "03n": "mdi-weather-cloudy",
        "04d": "mdi-weather-cloudy",
        "04n": "mdi-weather-cloudy",
        "09d": "mdi-weather-rainy",
        "09n": "mdi-weather-rainy",
        "10d": "mdi-weather-pouring",
        "10n": "mdi-weather-pouring",
        "11d": "mdi-weather-lightning",
        "11n": "mdi-weather-lightning",
        "13d": "mdi-weather-snowy",
        "13n": "mdi-weather-snowy",
        "50d": "mdi-weather-fog",
        "50n": "mdi-weather-fog",
    }
    return icon_map.get(icon_code, "mdi-weather-cloudy")


def get_wind_direction(degrees):
    """Convert degrees to cardinal direction."""
    if degrees is None:
        return "N"
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


def get_wind_icon(degrees):
    """Get arrow icon for wind direction."""
    if degrees is None:
        return "mdi-arrow-right"
    if 45 <= degrees < 135:
        return "mdi-arrow-left"
    elif 135 <= degrees < 225:
        return "mdi-arrow-up"
    elif 225 <= degrees < 315:
        return "mdi-arrow-right"
    else:
        return "mdi-arrow-down"


def hpa_to_inhg(hpa):
    """Convert hectopascals to inches of mercury."""
    return round(hpa * 0.02953, 2)


def meters_to_miles(meters):
    """Convert meters to miles."""
    return round(meters / 1609.34, 1)


def calculate_dew_point(temp_f, humidity):
    """Calculate dew point from temp (F) and humidity (%)."""
    temp_c = (temp_f - 32) * 5 / 9
    a, b = 17.27, 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + (humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)
    return round((dew_point_c * 9 / 5) + 32)


def get_moon_phase():
    """Calculate moon phase from date."""
    known_new_moon = datetime(2000, 1, 6)
    days_since = (datetime.now() - known_new_moon).days
    phase = (days_since % 29.53) / 29.53
    
    phases = [
        (0.0625, "New Moon"), (0.1875, "Waxing Crescent"),
        (0.3125, "First Quarter"), (0.4375, "Waxing Gibbous"),
        (0.5625, "Full Moon"), (0.6875, "Waning Gibbous"),
        (0.8125, "Last Quarter"), (0.9375, "Waning Crescent"),
        (1.0, "New Moon")
    ]
    for threshold, name in phases:
        if phase < threshold:
            return name
    return "New Moon"


def fetch_current_weather(lat, lon):
    """Fetch current conditions."""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "imperial"},
            timeout=10
        )
        response.raise_for_status()
        d = response.json()
        
        return {
            "temp": round(d["main"]["temp"]),
            "feels_like": round(d["main"]["feels_like"]),
            "temp_high": round(d["main"]["temp_max"]),
            "temp_low": round(d["main"]["temp_min"]),
            "condition": d["weather"][0]["main"],
            "icon": get_icon(d["weather"][0]["icon"]),
            "humidity": d["main"]["humidity"],
            "pressure": hpa_to_inhg(d["main"]["pressure"]),
            "wind_speed": round(d["wind"]["speed"]),
            "wind_direction": get_wind_direction(d["wind"].get("deg")),
            "visibility": meters_to_miles(d.get("visibility", 10000)),
            "dew_point": calculate_dew_point(d["main"]["temp"], d["main"]["humidity"]),
            "sunrise": datetime.fromtimestamp(d["sys"]["sunrise"]).strftime("%-I:%M %p").lower(),
            "sunset": datetime.fromtimestamp(d["sys"]["sunset"]).strftime("%-I:%M %p").lower(),
            "moon_phase": get_moon_phase(),
            "uv_index": 0,  # Not in free tier
        }
    except Exception as e:
        print(f"Error fetching current weather: {e}")
        return None


def fetch_air_quality(lat, lon):
    """Fetch air quality index."""
    try:
        response = requests.get(
            f"{BASE_URL}/air_pollution",
            params={"lat": lat, "lon": lon, "appid": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        d = response.json()
        
        aqi = d["list"][0]["main"]["aqi"]
        labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        values = {1: 25, 2: 50, 3: 100, 4: 150, 5: 200}
        
        return {"value": values.get(aqi, 50), "label": labels.get(aqi, "Unknown")}
    except Exception as e:
        print(f"Error fetching air quality: {e}")
        return None


def fetch_forecast(lat, lon):
    """
    Fetch 3-hour forecast data.
    Returns list of forecast points (3-hour intervals, ~16 points for 48 hours).
    """
    try:
        response = requests.get(
            f"{BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "imperial"},
            timeout=10
        )
        response.raise_for_status()
        d = response.json()
        
        forecasts = []
        for item in d["list"][:16]:  # 16 * 3 = 48 hours
            dt = datetime.fromtimestamp(item["dt"])
            wind_deg = item["wind"].get("deg")
            
            forecasts.append({
                "datetime": dt.isoformat(),
                "time": dt.strftime("%-I %p").lower(),
                "temp": round(item["main"]["temp"]),
                "feels_like": round(item["main"]["feels_like"]),
                "condition": item["weather"][0]["main"],
                "icon": get_icon(item["weather"][0]["icon"]),
                "precip_chance": round(item.get("pop", 0) * 100),
                "humidity": item["main"]["humidity"],
                "wind_speed": round(item["wind"]["speed"]),
                "wind_direction": get_wind_direction(wind_deg),
                "wind_icon": get_wind_icon(wind_deg),
                "pressure": hpa_to_inhg(item["main"]["pressure"]),
                "cloud_cover": item["clouds"]["all"],
                "visibility": meters_to_miles(item.get("visibility", 10000)),
                "precipitation": round(item.get("rain", {}).get("3h", 0) / 25.4, 2),
                "dew_point": calculate_dew_point(item["main"]["temp"], item["main"]["humidity"]),
                "uv_index": 0,
            })
        
        return forecasts
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return []


def group_forecast_by_date(forecast_data):
    """Group forecast data by date for display."""
    grouped = {}
    for item in forecast_data:
        dt = datetime.fromisoformat(item["datetime"])
        date_key = dt.strftime("%Y-%m-%d")
        date_display = dt.strftime("%A, %B %-d")
        
        if date_key not in grouped:
            grouped[date_key] = {"date": date_display, "hours": []}
        grouped[date_key]["hours"].append(item)
    
    return [grouped[k] for k in sorted(grouped.keys())]


def fetch_all_weather(lat, lon):
    """
    Fetch all weather data.
    Returns (current_data, forecast_list) tuple.
    """
    current = fetch_current_weather(lat, lon)
    forecast = fetch_forecast(lat, lon)
    air = fetch_air_quality(lat, lon)
    
    if current and air:
        current["air_quality"] = air["value"]
        current["air_quality_label"] = air["label"]
    
    return current, forecast