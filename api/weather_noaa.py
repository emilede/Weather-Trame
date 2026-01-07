"""
Weather API Integration
- NOAA (api.weather.gov) for forecasts and current conditions
- OpenWeatherMap for air quality only
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# OpenWeatherMap - only used for air quality
OWM_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OWM_URL = "https://api.openweathermap.org/data/2.5"

# NOAA - no API key needed
NOAA_URL = "https://api.weather.gov"
NOAA_HEADERS = {"User-Agent": "WeatherTrame/1.0 (weather-trame-app)"}


# =============================================================================
# Icon Mapping
# =============================================================================

def get_icon(noaa_condition):
    """Convert NOAA condition text to MDI icon."""
    condition = noaa_condition.lower() if noaa_condition else ""
    
    if "sunny" in condition or "clear" in condition:
        return "mdi-weather-sunny" if "night" not in condition else "mdi-weather-night"
    elif "partly cloudy" in condition or "partly sunny" in condition:
        return "mdi-weather-partly-cloudy"
    elif "cloudy" in condition or "overcast" in condition:
        return "mdi-weather-cloudy"
    elif "rain" in condition or "showers" in condition:
        return "mdi-weather-rainy"
    elif "thunderstorm" in condition or "storm" in condition:
        return "mdi-weather-lightning"
    elif "snow" in condition:
        return "mdi-weather-snowy"
    elif "fog" in condition or "mist" in condition:
        return "mdi-weather-fog"
    elif "wind" in condition:
        return "mdi-weather-windy"
    else:
        return "mdi-weather-cloudy"


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


# =============================================================================
# NOAA API Functions
# =============================================================================

def get_noaa_grid(lat, lon):
    """
    Get NOAA grid info for a location.
    Returns dict with forecast URLs or None on error.
    """
    try:
        response = requests.get(
            f"{NOAA_URL}/points/{lat},{lon}",
            headers=NOAA_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        props = response.json()["properties"]
        
        return {
            "grid_id": props["gridId"],
            "grid_x": props["gridX"],
            "grid_y": props["gridY"],
            "forecast_url": props["forecast"],
            "forecast_hourly_url": props["forecastHourly"],
            "observation_stations_url": props["observationStations"],
        }
    except Exception as e:
        print(f"Error getting NOAA grid: {e}")
        return None


def fetch_noaa_hourly(grid_info):
    """
    Fetch hourly forecast from NOAA.
    Returns list of hourly periods.
    """
    try:
        response = requests.get(
            grid_info["forecast_hourly_url"],
            headers=NOAA_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        periods = response.json()["properties"]["periods"]
        
        hourly_data = []
        for period in periods[:48]:  # 48 hours
            dt = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
            wind_deg = period.get("windDirection")
            # Convert cardinal to degrees for icon
            wind_deg_num = {"N": 0, "NNE": 22, "NE": 45, "ENE": 67, "E": 90, 
                          "ESE": 112, "SE": 135, "SSE": 157, "S": 180, 
                          "SSW": 202, "SW": 225, "WSW": 247, "W": 270, 
                          "WNW": 292, "NW": 315, "NNW": 337}.get(wind_deg, 0)
            
            # Parse wind speed (comes as "5 mph" string)
            wind_speed_str = period.get("windSpeed", "0 mph")
            wind_speed = int(wind_speed_str.split()[0]) if wind_speed_str else 0
            
            hourly_data.append({
                "datetime": dt.isoformat(),
                "time": dt.strftime("%-I %p").lower(),
                "temp": period["temperature"],
                "feels_like": period["temperature"],  # NOAA doesn't provide feels_like in hourly
                "condition": period["shortForecast"],
                "icon": get_icon(period["shortForecast"]),
                "precip_chance": period.get("probabilityOfPrecipitation", {}).get("value") or 0,
                "humidity": period.get("relativeHumidity", {}).get("value") or 0,
                "wind_speed": wind_speed,
                "wind_direction": wind_deg or "N",
                "wind_icon": get_wind_icon(wind_deg_num),
                "pressure": 30.0,  # NOAA doesn't include in hourly
                "cloud_cover": 0,  # Not in hourly forecast
                "visibility": 10,  # Not in hourly forecast
                "precipitation": 0,
                "dew_point": period.get("dewpoint", {}).get("value") or 0,
                "uv_index": 0,  # Not in hourly forecast
            })
        
        return hourly_data
    except Exception as e:
        print(f"Error fetching NOAA hourly: {e}")
        return []


def fetch_noaa_current(grid_info):
    """
    Fetch current conditions from nearest observation station.
    """
    try:
        # Get observation stations
        response = requests.get(
            grid_info["observation_stations_url"],
            headers=NOAA_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        stations = response.json()["features"]
        
        if not stations:
            return None
        
        # Get latest observation from first station
        station_id = stations[0]["properties"]["stationIdentifier"]
        obs_response = requests.get(
            f"{NOAA_URL}/stations/{station_id}/observations/latest",
            headers=NOAA_HEADERS,
            timeout=10
        )
        obs_response.raise_for_status()
        obs = obs_response.json()["properties"]
        
        # Convert units
        temp_c = obs.get("temperature", {}).get("value")
        temp_f = round(temp_c * 9/5 + 32) if temp_c is not None else None
        
        feels_c = obs.get("windChill", {}).get("value") or obs.get("heatIndex", {}).get("value") or temp_c
        feels_f = round(feels_c * 9/5 + 32) if feels_c is not None else temp_f
        
        dew_c = obs.get("dewpoint", {}).get("value")
        dew_f = round(dew_c * 9/5 + 32) if dew_c is not None else None
        
        wind_speed_kmh = obs.get("windSpeed", {}).get("value")
        wind_speed_mph = round(wind_speed_kmh * 0.621371) if wind_speed_kmh else 0
        
        pressure_pa = obs.get("barometricPressure", {}).get("value")
        pressure_inhg = round(pressure_pa * 0.00029530, 2) if pressure_pa else 30.0
        
        visibility_m = obs.get("visibility", {}).get("value")
        visibility_mi = round(visibility_m / 1609.34, 1) if visibility_m else 10
        
        wind_deg = obs.get("windDirection", {}).get("value")
        
        return {
            "temp": temp_f,
            "feels_like": feels_f,
            "temp_high": temp_f,  # Will update from daily forecast
            "temp_low": temp_f,   # Will update from daily forecast
            "condition": obs.get("textDescription") or "Unknown",
            "icon": get_icon(obs.get("textDescription")),
            "humidity": round(obs.get("relativeHumidity", {}).get("value") or 0),
            "pressure": pressure_inhg,
            "wind_speed": wind_speed_mph,
            "wind_direction": get_wind_direction(wind_deg),
            "visibility": visibility_mi,
            "dew_point": dew_f,
            "moon_phase": get_moon_phase(),
            "uv_index": 0,  # Not available from observations
        }
    except Exception as e:
        print(f"Error fetching NOAA current: {e}")
        return None


def fetch_noaa_daily(grid_info):
    """
    Fetch daily forecast to get high/low temps and sunrise/sunset.
    """
    try:
        response = requests.get(
            grid_info["forecast_url"],
            headers=NOAA_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        periods = response.json()["properties"]["periods"]
        
        # Find today's high and low
        today_high = None
        today_low = None
        
        for period in periods[:2]:  # First two periods (day/night)
            if period["isDaytime"]:
                today_high = period["temperature"]
            else:
                today_low = period["temperature"]
        
        return {
            "temp_high": today_high,
            "temp_low": today_low,
        }
    except Exception as e:
        print(f"Error fetching NOAA daily: {e}")
        return None


# =============================================================================
# OpenWeatherMap - Air Quality Only
# =============================================================================

def fetch_air_quality(lat, lon):
    """Fetch air quality from OpenWeatherMap."""
    try:
        response = requests.get(
            f"{OWM_URL}/air_pollution",
            params={"lat": lat, "lon": lon, "appid": OWM_API_KEY},
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


# =============================================================================
# Geocoding - Keep OpenWeatherMap for this
# =============================================================================

def search_cities(query, state="OR", country="US", limit=5):
    """Search for cities using OpenWeatherMap geocoding."""
    try:
        response = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": f"{query},{state},{country}",
                "limit": limit,
                "appid": OWM_API_KEY
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


# =============================================================================
# Main Functions
# =============================================================================

def fetch_all_weather(lat, lon):
    """
    Fetch all weather data from NOAA + air quality from OWM.
    Returns (current_data, hourly_data) tuple.
    """
    # Get NOAA grid info first
    grid_info = get_noaa_grid(lat, lon)
    if not grid_info:
        return None, []
    
    # Fetch all data
    current = fetch_noaa_current(grid_info)
    hourly = fetch_noaa_hourly(grid_info)
    daily = fetch_noaa_daily(grid_info)
    air = fetch_air_quality(lat, lon)
    
    # Merge daily into current
    if current and daily:
        if daily.get("temp_high"):
            current["temp_high"] = daily["temp_high"]
        if daily.get("temp_low"):
            current["temp_low"] = daily["temp_low"]
    
    # Add air quality
    if current and air:
        current["air_quality"] = air["value"]
        current["air_quality_label"] = air["label"]
    
    # Add sunrise/sunset (placeholder - would need separate API)
    if current:
        current["sunrise"] = "7:45 am"  # TODO: Calculate or fetch
        current["sunset"] = "4:50 pm"   # TODO: Calculate or fetch
    
    return current, hourly


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