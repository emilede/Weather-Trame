"""
Weather-Trame Application
Main entry point for the Trame-based weather dashboard
"""

from datetime import datetime, timezone

from trame.app import get_server
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3, html

from components.sidebar import create_sidebar
from pages.today import render_today_page
from pages.hourly import render_hourly_page
from pages.ten_day import render_ten_day_page
from pages.monthly import render_monthly_page
from pages.radar import render_radar_page
from api.weather_noaa import fetch_all_weather, group_forecast_by_date, search_cities

from components.radar_vtk import create_radar_renderer
from api.radar_processor import create_composite_grid

import pytz


# -----------------------------------------------------------------------------
# Trame Server Setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_weather_background(condition):
    """Get background URL based on condition."""
    if not condition:
        return "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&q=80"
    
    condition_lower = condition.lower()
    
    backgrounds = {
        "sunny": "https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=1200&q=80",
        "clear": "https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=1200&q=80",
        "cloudy": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&q=80",
        "partly": "https://images.unsplash.com/photo-1594156596782-656c93e4d504?w=1200&q=80",
        "overcast": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&q=80",
        "rain": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1200&q=80",
        "drizzle": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1200&q=80",
        "snow": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=1200&q=80",
        "fog": "https://images.unsplash.com/photo-1487621167305-5d248087c724?w=1200&q=80",
        "mist": "https://images.unsplash.com/photo-1487621167305-5d248087c724?w=1200&q=80",
        "storm": "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?w=1200&q=80",
        "thunder": "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?w=1200&q=80",
    }
    
    for key, url in backgrounds.items():
        if key in condition_lower:
            return url
    
    return "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&q=80"


# -----------------------------------------------------------------------------
# Initial State
# -----------------------------------------------------------------------------

state.current_page = "today"
state.location = {
    "name": "Portland, Oregon",
    "lat": 45.5152,
    "lon": -122.6784
}
state.search_query = ""
state.search_results = []
state.selected_city = None
state.weather_bg = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&q=80"

# Radar state - load VTK visualization (composite)
print("Loading radar data...")
from api.nexrad import get_oregon_radars

radar_files = get_oregon_radars()
if radar_files:
    radar_data = create_composite_grid(radar_files)
    if radar_data:
        radar_renderer, radar_render_window = create_radar_renderer(radar_data)
        pacific = pytz.timezone('America/Los_Angeles')
        radar_time_py = datetime(
            radar_data['time'].year,
            radar_data['time'].month,
            radar_data['time'].day,
            radar_data['time'].hour,
            radar_data['time'].minute,
            radar_data['time'].second,
            tzinfo=timezone.utc
        )
        state.radar_time_display = radar_time_py.astimezone(pacific).strftime("%b %d, %Y %I:%M %p PT")
        print(f"Radar loaded: {radar_data['grid'].shape} grid from {len(radar_data['stations'])} stations")
    else:
        print("WARNING: Could not create composite")
        radar_render_window = None
        state.radar_time_display = "No data available"
else:
    print("WARNING: Could not fetch radar data")
    radar_render_window = None
    state.radar_time_display = "No data available"


# -----------------------------------------------------------------------------
# Weather Data Functions
# -----------------------------------------------------------------------------

def load_weather_data(lat, lon):
    """Fetch and update weather data for given coordinates."""
    current_weather, forecast = fetch_all_weather(lat, lon)
    
    if current_weather:
        state.weather_data = current_weather
        state.weather_bg = get_weather_background(current_weather['condition'])
        print(f"Current weather: {current_weather['temp']}°F, {current_weather['condition']}")
    else:
        print("Failed to fetch current weather")
        return False
    
    if forecast:
        state.hourly_data = forecast
        state.hourly_grouped = group_forecast_by_date(forecast)
        state.hourly_preview = forecast[:4]
        print(f"Forecast loaded: {len(forecast)} data points")
    else:
        state.hourly_data = []
        state.hourly_grouped = []
        state.hourly_preview = []
    
    state.current_time_display = datetime.now().strftime("%-I:%M %p").strip()
    return True


@state.change("search_query")
def on_search_change(search_query, **kwargs):
    """React to search query changes."""
    if not search_query or len(search_query) < 2:
        state.search_results = []
        return
    
    results = search_cities(search_query)
    state.search_results = results


@state.change("selected_city")
def on_city_change(selected_city, **kwargs):
    """React to city selection."""
    if not selected_city:
        return
    
    state.location = {
        "name": selected_city["display_name"],
        "lat": selected_city["lat"],
        "lon": selected_city["lon"]
    }
    state.search_results = []
    state.selected_city = None
    
    print(f"Loading weather for {selected_city['display_name']}...")
    load_weather_data(selected_city["lat"], selected_city["lon"])


# Load initial weather data
print("Fetching weather data...")
if not load_weather_data(state.location["lat"], state.location["lon"]):
    print("API failed, using fallback data")
    state.weather_data = {
        "temp": 44,
        "feels_like": 44,
        "temp_high": 46,
        "temp_low": 38,
        "condition": "Clouds",
        "icon": "mdi-weather-cloudy",
        "humidity": 86,
        "wind_speed": 1,
        "wind_direction": "N",
        "air_quality": 60,
        "air_quality_label": "Fair",
        "pressure": 30.0,
        "uv_index": 0,
        "visibility": 6.2,
        "moon_phase": "Waxing Crescent",
        "sunrise": "7:45 am",
        "sunset": "4:48 pm",
        "dew_point": 40,
    }
    state.weather_bg = get_weather_background("Clouds")
    state.hourly_data = []
    state.hourly_grouped = []
    state.hourly_preview = []
    state.current_time_display = datetime.now().strftime("%-I:%M %p").strip()


# -----------------------------------------------------------------------------
# UI Layout
# -----------------------------------------------------------------------------

with VAppLayout(server, theme="dark") as layout:
    html.Style("""
        .date-header { 
            background-color: rgba(var(--v-theme-surface-variant), 0.3); 
        }
    """)
    
    with v3.VLayout():
        create_sidebar()
        
        with v3.VMain():
            with v3.VContainer(fluid=True, classes="pa-6"):
                with v3.VWindow(v_model=("current_page",)):
                    with v3.VWindowItem(value="today"):
                        render_today_page()
                    with v3.VWindowItem(value="hourly"):
                        render_hourly_page()
                    with v3.VWindowItem(value="ten_day"):
                        render_ten_day_page()
                    with v3.VWindowItem(value="monthly"):
                        render_monthly_page()
                    with v3.VWindowItem(value="radar"):
                        render_radar_page(radar_render_window, state.radar_time_display)


# -----------------------------------------------------------------------------
# Server Start
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()