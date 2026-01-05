"""
Sidebar Navigation Component
Weather.com style sidebar with navigation buttons
"""

from trame.widgets import vuetify3 as v3, html


def create_sidebar():
    """
    Creates the sidebar navigation with Vuetify's built-in navigation patterns.
    Uses v-model binding to update current_page state directly.
    """
    
    # Navigation items configuration
    nav_items = [
        {"icon": "mdi-weather-sunny", "label": "Today", "value": "today"},
        {"icon": "mdi-clock-outline", "label": "Hourly", "value": "hourly"},
        {"icon": "mdi-calendar-week", "label": "10 Day", "value": "ten_day"},
        {"icon": "mdi-calendar-month", "label": "Monthly", "value": "monthly"},
        {"icon": "mdi-radar", "label": "Radar", "value": "radar"},
    ]
    
    with v3.VNavigationDrawer(
        permanent=True,
        width=220,
    ):
        # Logo / Brand area
        with v3.VListItem(classes="pa-4"):
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-weather-partly-cloudy", size="32", color="primary")
                html.Span("Weather", classes="text-h6 ml-2 font-weight-bold")
        
        v3.VDivider()
        
        # Navigation List - click handlers directly update state
        with v3.VList(
            nav=True,
            density="comfortable",
            classes="pa-2"
        ):
            for item in nav_items:
                v3.VListItem(
                    prepend_icon=item["icon"],
                    title=item["label"],
                    value=item["value"],
                    active=(f"current_page === '{item['value']}'",),
                    click=f"current_page = '{item['value']}'",
                    rounded="lg",
                )
        
        v3.VDivider(classes="mt-2")
        
        # Additional sections (placeholders, non-functional for now)
        with v3.VList(density="compact", classes="pa-2"):
            with v3.VListGroup(value="severe"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VListItem(
                        v_bind="props",
                        prepend_icon="mdi-alert",
                        title="Severe Weather",
                    )
                v3.VListItem(title="Alerts", classes="pl-8", disabled=True)
                v3.VListItem(title="Warnings", classes="pl-8", disabled=True)
            
            with v3.VListGroup(value="health"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VListItem(
                        v_bind="props",
                        prepend_icon="mdi-heart-pulse",
                        title="Health & Wellness",
                    )
                v3.VListItem(title="Allergies", classes="pl-8", disabled=True)
                v3.VListItem(title="Flu", classes="pl-8", disabled=True)