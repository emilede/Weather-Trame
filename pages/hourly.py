"""
Hourly Page
48-hour detailed forecast view
"""

from trame.widgets import vuetify3 as v3, html


def render_hourly_page():
    """
    Renders the Hourly forecast page with:
    - Date headers that update as hours cross midnight
    - Expandable hourly rows with detailed weather info
    - 48 hours of forecast data
    """
    
    with html.Div():
        html.H1(
            "{{ location.name }} Weather",
            classes="text-h4 font-weight-bold mb-1"
        )
        html.Div(
            "As of {{ current_time_display }}",
            classes="text-body-2 text-medium-emphasis mb-4"
        )
        
        # Hourly forecast card
        with v3.VCard(elevation=1, rounded="lg"):
            with v3.VCardText(classes="pa-0"):
                # Use v-for with a div to group by date
                with html.Div(v_for="(group, groupIndex) in hourly_grouped", key="groupIndex"):
                    # Date header
                    html.Div(
                        "{{ group.date }}",
                        classes="date-header text-h6 font-weight-bold pa-4 pb-2 bg-surface-variant"
                    )
                    
                    # Hourly expansion panels for this date group
                    with v3.VExpansionPanels(variant="accordion"):
                        with v3.VExpansionPanel(
                            v_for="(hour, hourIndex) in group.hours",
                            key="hourIndex",
                        ):
                            # Panel Header (collapsed view)
                            with v3.VExpansionPanelTitle(classes="py-2"):
                                with v3.VRow(align="center", classes="w-100", no_gutters=True):
                                    with v3.VCol(cols=2, sm=1, classes="text-body-2"):
                                        html.Span("{{ hour.time }}")
                                    with v3.VCol(cols=2, sm=1):
                                        html.Span("{{ hour.temp }}°", classes="font-weight-bold")
                                    with v3.VCol(cols=2, sm=1):
                                        v3.VIcon("{{ hour.icon }}", size="28")
                                    with v3.VCol(cols=3, sm=2):
                                        html.Span("{{ hour.condition }}", classes="text-body-2")
                                    with v3.VCol(cols=2, sm=1):
                                        with html.Div(classes="d-flex align-center"):
                                            v3.VIcon("mdi-water-outline", size="16", classes="mr-1", color="info")
                                            html.Span("{{ hour.precip_chance }}%", classes="text-body-2")
                                    with v3.VCol(cols=3, sm=2, classes="d-none d-sm-flex align-center"):
                                        v3.VIcon("{{ hour.wind_icon }}", size="16", classes="mr-1")
                                        html.Span("{{ hour.wind_direction }} {{ hour.wind_speed }} mph", classes="text-body-2")
                            
                            # Panel Content (expanded view)
                            with v3.VExpansionPanelText():
                                with v3.VRow(classes="pa-2"):
                                    # Row of detail items
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-thermometer", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("Feels Like", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.feels_like }}°", classes="text-body-2 font-weight-medium")
                                    
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-weather-windy", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("Wind", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.wind_direction }} {{ hour.wind_speed }} mph", classes="text-body-2 font-weight-medium")
                                    
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-water-percent", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("Humidity", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.humidity }}%", classes="text-body-2 font-weight-medium")
                                    
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-white-balance-sunny", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("UV Index", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.uv_index }} of 11", classes="text-body-2 font-weight-medium")
                                    
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-cloud-outline", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("Cloud Cover", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.cloud_cover }}%", classes="text-body-2 font-weight-medium")
                                    
                                    with v3.VCol(cols=6, sm=4, md=2):
                                        with html.Div(classes="py-1"):
                                            with html.Div(classes="d-flex align-center mb-1"):
                                                v3.VIcon("mdi-umbrella-outline", size="16", classes="mr-1 text-medium-emphasis")
                                                html.Span("Precip Amount", classes="text-caption text-medium-emphasis")
                                            html.Div("{{ hour.precipitation }} in", classes="text-body-2 font-weight-medium")