"""
Weather-Trame Application
Main entry point for the Trame-based weather dashboard
"""

from datetime import datetime, timedelta
import random

from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3, html

from components.sidebar import create_sidebar
from pages.today import render_today_page
from pages.hourly import render_hourly_page
from pages.ten_day import render_ten_day_page
from pages.monthly import render_monthly_page
from pages.radar import render_radar_page


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def generate_hourly_data(hours=48):
    """
    Generate mock hourly weather data starting from the current hour.
    Returns a flat list of hourly data.
    """
    now = datetime.now()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    
    conditions = [
        ("Cloudy", "mdi-weather-cloudy"),
        ("Mostly Cloudy", "mdi-weather-partly-cloudy"),
        ("Partly Cloudy", "mdi-weather-partly-cloudy"),
        ("Sunny", "mdi-weather-sunny"),
        ("Clear", "mdi-weather-night"),
    ]
    
    wind_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "NNE", "SSW", "WSW", "WNW"]
    
    hourly_data = []
    base_temp = 38
    
    for i in range(hours):
        hour_dt = current_hour + timedelta(hours=i)
        hour_of_day = hour_dt.hour
        
        # Simulate temperature variation (cooler at night, warmer midday)
        temp_offset = -5 if hour_of_day < 6 or hour_of_day > 20 else (3 if 10 <= hour_of_day <= 16 else 0)
        temp = base_temp + temp_offset + random.randint(-2, 2)
        
        # Pick condition based on time (clear at night, cloudier during day)
        if hour_of_day < 6 or hour_of_day > 20:
            condition, icon = ("Clear", "mdi-weather-night")
        else:
            condition, icon = random.choice(conditions[:3])  # Cloudy variants during day
        
        # Format time
        time_str = hour_dt.strftime("%-I %p").lower()  # "1 pm", "2 am", etc.
        
        # Wind icon based on direction
        wind_dir = random.choice(wind_directions)
        wind_icon = "mdi-arrow-up" if "N" in wind_dir else "mdi-arrow-down" if "S" in wind_dir else "mdi-arrow-right"
        
        hourly_data.append({
            "datetime": hour_dt.isoformat(),
            "time": time_str,
            "temp": temp,
            "condition": condition,
            "icon": icon,
            "precip_chance": random.randint(0, 15),
            "humidity": random.randint(75, 98),
            "wind_speed": random.randint(1, 8),
            "wind_direction": wind_dir,
            "wind_icon": wind_icon,
            "precipitation": 0,
            "feels_like": temp - random.randint(2, 5),
            "pressure": round(29.8 + random.random() * 0.3, 2),
            "cloud_cover": random.randint(40, 100),
            "dew_point": temp - random.randint(3, 8),
            "uv_index": 0 if hour_of_day < 7 or hour_of_day > 18 else random.randint(0, 3),
            "visibility": random.randint(7, 10),
            "air_quality": random.randint(20, 35),
            "air_quality_label": "Good",
            "wind_gust": None,
        })
    
    return hourly_data


def group_hourly_by_date(hourly_data):
    """
    Group hourly data by date for display with date headers.
    Returns a list of {date: "Monday, January 5", hours: [...]}
    """
    grouped = {}
    
    for hour in hourly_data:
        dt = datetime.fromisoformat(hour["datetime"])
        date_key = dt.strftime("%Y-%m-%d")
        date_display = dt.strftime("%A, %B %-d")  # "Monday, January 5"
        
        if date_key not in grouped:
            grouped[date_key] = {
                "date": date_display,
                "hours": []
            }
        grouped[date_key]["hours"].append(hour)
    
    # Return as sorted list
    return [grouped[key] for key in sorted(grouped.keys())]

# -----------------------------------------------------------------------------
# Trame Server Setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Initial State
# -----------------------------------------------------------------------------

state.current_page = "today"
state.location = {
    "name": "Oregon, Oregon",
    "lat": 44.0521,
    "lon": -123.0868
}

# Mock weather data (will be replaced with API data later)
state.weather_data = {
    "temp": 38,
    "feels_like": 34,
    "temp_high": 39,
    "temp_low": 29,
    "condition": "Cloudy",
    "icon": "cloudy",
    "humidity": 84,
    "wind_speed": 5,
    "wind_direction": "S",
    "air_quality": 27,
    "air_quality_label": "Good",
    "pressure": 29.91,
    "uv_index": 1,
    "visibility": 8,
    "moon_phase": "Waning Gibbous",
    "sunrise": "7:37 am",
    "sunset": "4:39 pm",
    "dew_point": 34,
}

state.hourly_data = generate_hourly_data(48)
state.hourly_grouped = group_hourly_by_date(state.hourly_data)
state.hourly_preview = state.hourly_data[:4]  # First 4 hours for Today page
state.current_time_display = datetime.now().strftime("%-I:%M %p %Z").strip()

# -----------------------------------------------------------------------------
# UI Layout
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.title.set_text("Weather-Trame")
    
    # Hide default toolbar
    layout.toolbar.hide()
    
    with layout.content:
        # Minimal custom CSS - only for things Vuetify can't handle
        html.Style("""
            .current-conditions-card { 
                background: linear-gradient(135deg, #4a6fa5 0%, #2d3a4a 100%) !important; 
            }
            .date-header { 
                background-color: rgba(var(--v-theme-surface-variant), 0.3); 
            }
        """)
        
        with v3.VApp(theme="dark"):
            with v3.VLayout():
                # Sidebar
                create_sidebar()
                
                # Main Content Area - VMain automatically adjusts for navigation drawer
                with v3.VMain():
                    with v3.VContainer(fluid=True, classes="pa-6"):
                        # Page Router - shows different page based on state.current_page
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
                                render_radar_page()


# -----------------------------------------------------------------------------
# Server Start
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()