"""
Radar Page
Interactive radar map (placeholder for now)
"""

from trame.widgets import vuetify3 as v3, html


def render_radar_page():
    """
    Placeholder for the Radar page.
    Will show interactive radar map with weather overlays.
    """
    
    with html.Div(classes="radar-page"):
        html.H1(
            "Weather Radar",
            classes="text-h4 font-weight-bold mb-4 white--text"
        )
        
        with v3.VCard(classes="placeholder-card", elevation=0):
            with v3.VCardText(classes="pa-8 text-center"):
                v3.VIcon(
                    "mdi-radar",
                    size="64",
                    color="grey",
                    classes="mb-4"
                )
                html.Div(
                    "Weather Radar Coming Soon",
                    classes="text-h6 grey--text"
                )
                html.Div(
                    "This page will show interactive radar with precipitation overlays",
                    classes="text-body-2 grey--text mt-2"
                )
