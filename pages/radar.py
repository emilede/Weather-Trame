"""
Radar Page - Simple image display
"""

from trame.widgets import vuetify3 as v3, html
from api.radar import get_radar_url, get_basemap_url


def render_radar_page():
    """Renders the Radar page with NEXRAD imagery."""
    
    radar_url = get_radar_url()
    basemap_url = get_basemap_url()
    
    with html.Div():
        html.H1(
            "Weather Radar",
            classes="text-h4 font-weight-bold mb-4"
        )
        
        # Radar timestamp display
        with html.Div(classes="d-flex align-center mb-4"):
            v3.VIcon("mdi-clock-outline", size="20", classes="mr-2")
            html.Span("{{ radar_time }}", classes="text-body-1")
        
        # Radar view card
        with v3.VCard(elevation=2, rounded="lg", classes="mb-4"):
            with html.Div(style="position: relative; height: 500px; width: 100%; background: #1a1a2e;"):
                # Basemap layer
                html.Img(
                    src=basemap_url,
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.5;"
                )
                # Radar layer (uses radar_key for cache busting)
                html.Img(
                    src=(f"'{radar_url}&t=' + radar_key",),
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                )
        
        # Controls
        with v3.VCard(elevation=1, rounded="lg", classes="pa-4"):
            with v3.VRow(align="center", justify="center"):
                with v3.VCol(cols="auto"):
                    v3.VBtn(
                        "Refresh",
                        prepend_icon="mdi-refresh",
                        variant="tonal",
                        click="radar_key = Date.now()"
                    )
            
            # Legend
            with html.Div(classes="mt-4"):
                html.Div("Reflectivity (dBZ)", classes="text-caption text-medium-emphasis mb-2")
                with html.Div(classes="d-flex align-center"):
                    html.Div(
                        style="height: 16px; width: 100%; border-radius: 4px; "
                              "background: linear-gradient(to right, "
                              "#00ff00 0%, #ffff00 25%, #ff9900 50%, #ff0000 75%, #ff00ff 100%);"
                    )
                with html.Div(classes="d-flex justify-space-between text-caption text-medium-emphasis mt-1"):
                    html.Span("5 dBZ")
                    html.Span("25 dBZ")
                    html.Span("40 dBZ")
                    html.Span("65+ dBZ")
        
        # Info
        with v3.VCard(elevation=1, rounded="lg", classes="pa-4 mt-4"):
            with html.Div(classes="text-body-2 text-medium-emphasis"):
                html.Span("NEXRAD N0Q Composite Reflectivity from ")
                html.A(
                    "Iowa State Mesonet",
                    href="https://mesonet.agron.iastate.edu/",
                    target="_blank",
                    classes="text-primary"
                )