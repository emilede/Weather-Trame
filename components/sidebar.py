"""
Sidebar Navigation Component
Weather.com style sidebar with navigation buttons
"""

from trame.widgets import vuetify3 as v3, html


def create_sidebar():
    """
    Creates the sidebar navigation with Vuetify's built-in navigation patterns.
    Includes search bar for Oregon cities.
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
        width=260,
    ):
        # Logo / Brand area
        with v3.VListItem(classes="pa-4"):
            with html.Div(classes="d-flex align-center"):
                v3.VIcon("mdi-weather-partly-cloudy", size="32", color="primary")
                html.Span("Weather", classes="text-h6 ml-2 font-weight-bold")
        
        v3.VDivider()
        
        # Search Section
        with html.Div(classes="pa-3"):
            v3.VTextField(
                v_model=("search_query",),
                label="Search Oregon cities",
                prepend_inner_icon="mdi-magnify",
                density="compact",
                variant="outlined",
                hide_details=True,
                clearable=True,
            )
            
            # Search Results Dropdown
            with v3.VList(
                v_if="search_results.length > 0",
                density="compact",
                classes="mt-2 rounded border",
            ):
                v3.VListItem(
                    v_for="(city, index) in search_results",
                    key="index",
                    title=("city.display_name",),
                    prepend_icon="mdi-map-marker",
                    click="selected_city = city; search_query = ''",
                )
        
        v3.VDivider()
        
        # Current Location Display
        with html.Div(classes="pa-3"):
            with html.Div(classes="d-flex align-center text-caption text-medium-emphasis"):
                v3.VIcon("mdi-map-marker", size="16", classes="mr-1")
                html.Span("{{ location.name }}")
        
        v3.VDivider()
        
        # Navigation List
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