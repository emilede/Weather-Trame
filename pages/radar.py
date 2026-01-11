"""
Radar Page - VTK NEXRAD visualization
"""

from trame.widgets import vuetify3 as v3, vtk as vtk_widgets, html


def render_radar_page(render_window, radar_time):
    """
    Renders the Radar page with VTK visualization.
    """
    
    with html.Div():
        # Header
        html.H1(
            "Portland, Oregon Radar Map",
            classes="text-h5 font-weight-bold mb-4 text-center"
        )
        
        # Horizontal Legend Bar
        with html.Div(classes="d-flex justify-center align-center mb-4 ga-6"):
            # Rain
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-water-outline", size="18", classes="mr-1")
                html.Span("Rain", classes="text-body-2 mr-2")
                html.Div(
                    style="width: 80px; height: 12px; border-radius: 6px; "
                          "background: linear-gradient(to right, #00ff00, #ffff00, #ff9900, #ff0000);"
                )
            
            # Freezing Rain
            with html.Div(classes="d-flex align-center"):
                html.Span("Frz Rain", classes="text-body-2 mr-2")
                html.Div(
                    style="width: 80px; height: 12px; border-radius: 6px; "
                          "background: linear-gradient(to right, #ff69b4, #c71585);"
                )
            
            # Mix
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-snowflake-variant", size="18", classes="mr-1")
                html.Span("Mix", classes="text-body-2 mr-2")
                html.Div(
                    style="width: 80px; height: 12px; border-radius: 6px; "
                          "background: linear-gradient(to right, #40e0d0, #008b8b);"
                )
            
            # Snow
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-snowflake", size="18", classes="mr-1")
                html.Span("Snow", classes="text-body-2 mr-2")
                html.Div(
                    style="width: 80px; height: 12px; border-radius: 6px; "
                          "background: linear-gradient(to right, #add8e6, #4169e1);"
                )
        
        # Timestamp
        with html.Div(classes="d-flex justify-center align-center mb-2"):
            v3.VIcon("mdi-clock-outline", size="18", classes="mr-2 text-medium-emphasis")
            html.Span(radar_time, classes="text-body-2 text-medium-emphasis")
        
        # Radar view card
        with v3.VCard(elevation=2, rounded="lg", classes="mb-4"):
            with html.Div(style="height: 600px; width: 100%;"):
                vtk_widgets.VtkRemoteView(
                    render_window,
                    interactive_ratio=1,
                    interactive_quality=80,
                )