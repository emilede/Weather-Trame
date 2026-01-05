"""
Monthly Page
Monthly weather overview (placeholder for now)
"""

from trame.widgets import vuetify3 as v3, html


def render_monthly_page():
    """
    Placeholder for the Monthly weather page.
    Will show monthly calendar with weather trends.
    """
    
    with html.Div(classes="monthly-page"):
        html.H1(
            "Monthly Forecast",
            classes="text-h4 font-weight-bold mb-4 white--text"
        )
        
        with v3.VCard(classes="placeholder-card", elevation=0):
            with v3.VCardText(classes="pa-8 text-center"):
                v3.VIcon(
                    "mdi-calendar-month",
                    size="64",
                    color="grey",
                    classes="mb-4"
                )
                html.Div(
                    "Monthly Forecast Coming Soon",
                    classes="text-h6 grey--text"
                )
                html.Div(
                    "This page will show monthly weather calendar and trends",
                    classes="text-body-2 grey--text mt-2"
                )
