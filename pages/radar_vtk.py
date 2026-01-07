"""
Radar Page
VTK-based NEXRAD radar visualization
"""

from trame.widgets import vuetify3 as v3, vtk as vtk_widgets, html


def render_radar_page(render_window, ctrl):
    """
    Renders the Radar page with VTK visualization.
    
    Args:
        render_window: VTK render window from radar visualization
        ctrl: Trame controller for binding functions
    """
    
    with html.Div():
        html.H1(
            "Weather Radar",
            classes="text-h4 font-weight-bold mb-4"
        )
        
        # Radar timestamp display
        with html.Div(classes="d-flex align-center mb-4"):
            v3.VIcon("mdi-clock-outline", size="20", classes="mr-2")
            html.Span("{{ radar_time_display }}", classes="text-body-1")
        
        # Radar view card
        with v3.VCard(elevation=2, rounded="lg", classes="mb-4"):
            # VTK View
            with html.Div(style="height: 500px; width: 100%;"):
                view = vtk_widgets.VtkLocalView(render_window)
                ctrl.radar_view_update = view.update
        
        # Controls
        with v3.VCard(elevation=1, rounded="lg", classes="pa-4"):
            with v3.VRow(align="center"):
                # Play/Pause button
                with v3.VCol(cols="auto"):
                    with v3.VBtn(
                        icon=True,
                        click="radar_playing = !radar_playing",
                        variant="tonal",
                    ):
                        v3.VIcon("{{ radar_playing ? 'mdi-pause' : 'mdi-play' }}")
                
                # Time slider
                with v3.VCol():
                    v3.VSlider(
                        v_model=("radar_frame_index",),
                        min=0,
                        max=("radar_max_frames",),
                        step=1,
                        hide_details=True,
                        thumb_label=True,
                    )
                
                # Refresh button
                with v3.VCol(cols="auto"):
                    with v3.VBtn(
                        icon=True,
                        click=ctrl.refresh_radar,
                        variant="tonal",
                    ):
                        v3.VIcon("mdi-refresh")
            
            # Legend
            with html.Div(classes="mt-4"):
                html.Div("Reflectivity (dBZ)", classes="text-caption text-medium-emphasis mb-2")
                with html.Div(classes="d-flex align-center"):
                    # Color scale
                    html.Div(
                        style="height: 16px; width: 100%; border-radius: 4px; "
                              "background: linear-gradient(to right, "
                              "#00ff00 0%, #ffff00 25%, #ff9900 50%, #ff0000 75%, #ff00ff 100%);"
                    )
                with html.Div(classes="d-flex justify-space-between text-caption text-medium-emphasis mt-1"):
                    html.Span("Light")
                    html.Span("Moderate")
                    html.Span("Heavy")
                    html.Span("Severe")