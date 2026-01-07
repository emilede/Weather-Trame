"""
Weather-Trame Application
Main entry point for the Trame-based weather dashboard
"""

from datetime import datetime, timezone

from trame.app import get_server, asynchronous
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3, html

from components.sidebar import create_sidebar
from pages.today import render_today_page
from pages.hourly import render_hourly_page
from pages.ten_day import render_ten_day_page
from pages.monthly import render_monthly_page
from pages.radar import render_radar_page
from api.weather_noaa import fetch_all_weather, group_forecast_by_date, search_cities
from api.radar import RadarVisualization


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
    "name": "Portland, Oregon",
    "lat": 45.5152,
    "lon": -122.6784
}
state.search_query = ""
state.search_results = []
state.selected_city = None

# Radar state
state.radar_frame_index = 0
state.radar_max_frames = 11  # 0-11 = 12 frames
state.radar_playing = False
state.radar_time_display = "Loading..."


# -----------------------------------------------------------------------------
# Radar Visualization Setup
# -----------------------------------------------------------------------------

radar_viz = RadarVisualization()
radar_initialized = False


@ctrl.add("refresh_radar")
def refresh_radar():
    """Refresh radar data from server."""
    global radar_initialized
    print("Refreshing radar data...")
    radar_viz.load_timestamps(12)
    state.radar_frame_index = len(radar_viz.timestamps) - 1
    update_radar_frame()
    radar_initialized = True


def update_radar_frame():
    """Update the radar visualization to current frame."""
    if radar_viz.update_frame(state.radar_frame_index):
        state.radar_time_display = radar_viz.get_current_time_str()
        if hasattr(ctrl, 'radar_view_update'):
            ctrl.radar_view_update()


@state.change("radar_frame_index")
def on_radar_frame_change(radar_frame_index, **kwargs):
    """React to radar frame slider changes."""
    if radar_initialized:
        update_radar_frame()


@state.change("radar_playing")
def on_radar_play_change(radar_playing, **kwargs):
    """Handle play/pause state changes."""
    if radar_playing and radar_initialized:
        advance_radar_animation()


@state.change("current_page")
def on_page_change(current_page, **kwargs):
    """Initialize radar when user navigates to radar page."""
    global radar_initialized
    if current_page == "radar" and not radar_initialized:
        print("Initializing radar on first visit...")
        radar_viz.load_timestamps(12)
        state.radar_frame_index = len(radar_viz.timestamps) - 1
        update_radar_frame()
        radar_initialized = True


@asynchronous.task
async def advance_radar_animation():
    """Animate through radar frames."""
    import asyncio
    while state.radar_playing:
        await asyncio.sleep(0.5)  # 500ms between frames
        if state.radar_frame_index < state.radar_max_frames:
            state.radar_frame_index += 1
        else:
            state.radar_frame_index = 0  # Loop back
        state.flush()


# -----------------------------------------------------------------------------
# Weather Data Functions
# -----------------------------------------------------------------------------

def load_weather_data(lat, lon):
    """Fetch and update weather data for given coordinates."""
    current_weather, forecast = fetch_all_weather(lat, lon)
    
    if current_weather:
        state.weather_data = current_weather
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
    state.selected_city = None  # Reset for next selection
    
    print(f"Loading weather for {selected_city['display_name']}...")
    load_weather_data(selected_city["lat"], selected_city["lon"])


# Load initial weather data
print("Fetching weather data...")
if not load_weather_data(state.location["lat"], state.location["lon"]):
    # Fallback mock data if API fails
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
    state.hourly_data = []
    state.hourly_grouped = []
    state.hourly_preview = []
    state.current_time_display = datetime.now().strftime("%-I:%M %p").strip()


# -----------------------------------------------------------------------------
# UI Layout
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.title.set_text("Weather-Trame")
    
    # Hide default toolbar
    layout.toolbar.hide()
    
    with layout.content:
        # Minimal custom CSS - only for gradient card
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
                
                # Main Content Area
                with v3.VMain():
                    with v3.VContainer(fluid=True, classes="pa-6"):
                        # Page Router
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
                                render_radar_page(radar_viz.render_window, ctrl)


# -----------------------------------------------------------------------------
# Server Start
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()