"""
Today Page
Main weather dashboard showing current conditions and hourly forecast
"""

from trame.widgets import vuetify3 as v3, html


def render_today_page():
    """
    Renders the Today page with:
    - Location header
    - Current conditions hero card with dynamic background
    - Details grid (wind, humidity, etc.)
    - Hourly forecast with expandable cards
    """
    
    with html.Div():
        # Location Header
        html.H1(
            "{{ location.name }} Weather",
            classes="text-h4 font-weight-bold mb-4"
        )
        
        # Current Conditions Hero Card with dynamic background
        with v3.VCard(
            classes="mb-6", 
            elevation=0, 
            rounded="lg",
            style=("'background: linear-gradient(to right, rgba(0,0,0,0.6), rgba(0,0,0,0.3)), url(' + weather_bg + '); background-size: cover; background-position: center;'",),
        ):
            with v3.VCardText(classes="pa-6"):
                with v3.VRow(align="center"):
                    # Weather Icon
                    with v3.VCol(cols="auto"):
                        v3.VIcon(
                            "{{ weather_data.icon }}",
                            size="80",
                        )
                    # Temperature
                    with v3.VCol(cols="auto"):
                        html.Span(
                            "{{ weather_data.temp }}°",
                            classes="text-h1 font-weight-bold"
                        )
                
                # Condition text
                html.Div(
                    "{{ weather_data.condition }}",
                    classes="text-h5 mt-2"
                )
                
                # Feels like / Day / Night
                html.Div(
                    "Feels Like {{ weather_data.feels_like }}° · "
                    "Day {{ weather_data.temp_high }}° · "
                    "Night {{ weather_data.temp_low }}°",
                    classes="text-body-1 text-medium-emphasis mt-1"
                )
        
        # Details Grid
        with v3.VCard(classes="mb-6", elevation=1, rounded="lg"):
            with v3.VCardText(classes="pa-4"):
                with v3.VRow():
                    # Left column
                    with v3.VCol(cols=6):
                        _detail_row("mdi-weather-windy", "Wind", "{{ weather_data.wind_speed }} mph {{ weather_data.wind_direction }}")
                        _detail_row("mdi-air-filter", "Air Quality", "{{ weather_data.air_quality }} - {{ weather_data.air_quality_label }}")
                        _detail_row("mdi-gauge", "Pressure", "{{ weather_data.pressure }} in")
                        _detail_row("mdi-eye", "Visibility", "{{ weather_data.visibility }} mi")
                        _detail_row("mdi-weather-sunset-up", "Sunrise", "{{ weather_data.sunrise }}")
                    
                    # Right column
                    with v3.VCol(cols=6):
                        _detail_row("mdi-water-percent", "Humidity", "{{ weather_data.humidity }}%")
                        _detail_row("mdi-thermometer-water", "Dew Point", "{{ weather_data.dew_point }}°")
                        _detail_row("mdi-sun-wireless", "UV Index", "{{ weather_data.uv_index }} of 11")
                        _detail_row("mdi-moon-waning-gibbous", "Moon Phase", "{{ weather_data.moon_phase }}")
                        _detail_row("mdi-weather-sunset-down", "Sunset", "{{ weather_data.sunset }}")
        
        # Hourly Weather Section
        html.H2("Hourly Weather", classes="text-h5 font-weight-bold mb-3")
        
        with v3.VCard(elevation=1, rounded="lg"):
            with v3.VCardText(classes="pa-0"):
                # Condition label
                with html.Div(classes="pa-4 pb-2"):
                    with html.Div(classes="d-flex align-center"):
                        v3.VIcon("{{ weather_data.icon }}", size="20", color="primary", classes="mr-2")
                        html.Span("{{ weather_data.condition }}", classes="text-primary")
                
                # Hourly expansion panels
                with v3.VExpansionPanels(variant="accordion", classes="hourly-panels"):
                    with v3.VExpansionPanel(
                        v_for="(hour, index) in hourly_preview",
                        key="index",
                        classes="hourly-panel",
                    ):
                        # Panel Header
                        with v3.VExpansionPanelTitle(classes="hourly-panel-header"):
                            with v3.VRow(align="center", classes="w-100"):
                                with v3.VCol(cols=1, classes="text-body-2"):
                                    html.Span("{{ hour.time }}")
                                with v3.VCol(cols=1):
                                    html.Span("{{ hour.temp }}°", classes="font-weight-bold")
                                with v3.VCol(cols=1):
                                    v3.VIcon("{{ hour.icon }}", size="24")
                                with v3.VCol(cols=2):
                                    html.Span("{{ hour.condition }}", classes="text-body-2")
                                with v3.VCol(cols=1):
                                    with html.Div(classes="d-flex align-center"):
                                        v3.VIcon("mdi-water", size="16", classes="mr-1", color="blue")
                                        html.Span("{{ hour.precip_chance }}%", classes="text-body-2")
                                with v3.VCol(cols=2):
                                    with html.Div():
                                        html.Div("Humidity", classes="text-caption opacity-60")
                                        html.Div("{{ hour.humidity }}%", classes="text-body-2")
                                with v3.VCol(cols=2):
                                    with html.Div():
                                        html.Div("Wind", classes="text-caption opacity-60")
                                        html.Div("{{ hour.wind_speed }} mph", classes="text-body-2")
                                with v3.VCol(cols=2):
                                    with html.Div():
                                        html.Div("Precipitation", classes="text-caption opacity-60")
                                        html.Div("{{ hour.precipitation }} in", classes="text-body-2")
                        
                        # Panel Content
                        with v3.VExpansionPanelText():
                            with v3.VRow(classes="pa-2"):
                                _hourly_detail("Feels Like", "{{ hour.feels_like }}°")
                                _hourly_detail("Precip Amount", "{{ hour.precipitation }} in")
                                _hourly_detail("Wind", "{{ hour.wind_speed }} mph {{ hour.wind_direction }}")
                                _hourly_detail("Pressure", "{{ hour.pressure }} in")
                                
                            with v3.VRow(classes="pa-2"):
                                _hourly_detail("Cloud Cover", "{{ hour.cloud_cover }}%")
                                _hourly_detail("Dew Point", "{{ hour.dew_point }}°")
                                _hourly_detail("UV Index", "{{ hour.uv_index }} of 11")
                                _hourly_detail("Visibility", "{{ hour.visibility }} mi")


def _detail_row(icon, label, value):
    """Helper to create a detail row in the grid"""
    with html.Div(classes="d-flex align-center py-3 border-b-thin"):
        v3.VIcon(icon, size="20", classes="mr-3 text-medium-emphasis")
        html.Span(label, classes="text-medium-emphasis flex-grow-1")
        html.Span(value, classes="font-weight-medium")


def _hourly_detail(label, value):
    """Helper to create an hourly detail item"""
    with v3.VCol(cols=3):
        with html.Div(classes="py-1"):
            html.Div(label, classes="text-caption text-medium-emphasis")
            html.Div(value, classes="text-body-2")
