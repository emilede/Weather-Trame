"""
Sidebar Navigation Component
Weather.com style sidebar with navigation buttons
"""

from trame.widgets import vuetify3 as v3, html


def create_sidebar():
    """
    Creates the sidebar navigation with weather.com styling.
    Buttons trigger page navigation via the navigate_to controller.
    """
    
    # Navigation items configuration
    nav_items = [
        {"icon": "mdi-weather-sunny", "label": "Today", "page": "today"},
        {"icon": "mdi-clock-outline", "label": "Hourly", "page": "hourly"},
        {"icon": "mdi-calendar-week", "label": "10 Day", "page": "ten_day"},
        {"icon": "mdi-calendar-month", "label": "Monthly", "page": "monthly"},
        {"icon": "mdi-radar", "label": "Radar", "page": "radar"},
    ]
    
    with v3.VNavigationDrawer(
        permanent=True,
        width="220",
        classes="sidebar",
    ):
        # Logo / Brand area
        with v3.VListItem(classes="sidebar-header pa-4"):
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-weather-partly-cloudy", size="32", color="white")
                html.Span("Weather", classes="text-h6 ml-2 font-weight-bold white--text")
        
        v3.VDivider(classes="sidebar-divider")
        
        # Navigation List
        with v3.VList(nav=True, density="comfortable", classes="pa-2"):
            for item in nav_items:
                v3.VListItem(
                    prepend_icon=item["icon"],
                    title=item["label"],
                    value=item["page"],
                    active=f"current_page === '{item['page']}'",
                    click=f"navigate_to('{item['page']}')",
                    classes="sidebar-nav-item mb-1",
                    rounded="lg",
                )
        
        v3.VDivider(classes="sidebar-divider mt-2")
        
        # Additional sections (placeholders, non-functional for now)
        with v3.VList(density="compact", classes="pa-2"):
            with v3.VListGroup(value="severe"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VListItem(
                        v_bind="props",
                        prepend_icon="mdi-alert",
                        title="Severe Weather",
                        classes="sidebar-nav-item",
                    )
                v3.VListItem(title="Alerts", classes="pl-8", disabled=True)
                v3.VListItem(title="Warnings", classes="pl-8", disabled=True)
            
            with v3.VListGroup(value="health"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VListItem(
                        v_bind="props",
                        prepend_icon="mdi-heart-pulse",
                        title="Health & Wellness",
                        classes="sidebar-nav-item",
                    )
                v3.VListItem(title="Allergies", classes="pl-8", disabled=True)
                v3.VListItem(title="Flu", classes="pl-8", disabled=True)
