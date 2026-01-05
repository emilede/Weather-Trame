"""
10 Day Page
Extended 10-day forecast view (placeholder for now)
"""

from trame.widgets import vuetify3 as v3, html


def render_ten_day_page():
    """
    Placeholder for the 10-day forecast page.
    Will show extended forecast with daily highs/lows.
    """
    
    with html.Div(classes="ten-day-page"):
        html.H1(
            "10 Day Forecast",
            classes="text-h4 font-weight-bold mb-4 white--text"
        )
        
        with v3.VCard(classes="placeholder-card", elevation=0):
            with v3.VCardText(classes="pa-8 text-center"):
                v3.VIcon(
                    "mdi-calendar-week",
                    size="64",
                    color="grey",
                    classes="mb-4"
                )
                html.Div(
                    "10 Day Forecast Coming Soon",
                    classes="text-h6 grey--text"
                )
                html.Div(
                    "This page will show extended forecast with daily details",
                    classes="text-body-2 grey--text mt-2"
                )
