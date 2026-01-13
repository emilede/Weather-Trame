"""
Radar VTK Visualization
Creates VTK actors from radar data - image-based rendering with precip type colors
"""

import numpy as np
from vtkmodules.vtkCommonCore import vtkUnsignedCharArray
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkImageSlice,
    vtkImageSliceMapper,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
import vtkmodules.vtkRenderingOpenGL2  # noqa


class MapInteractorStyle(vtkInteractorStyleImage):
    """Custom interactor: left-click pans, scroll zooms."""
    
    def __init__(self):
        super().__init__()
        self.AddObserver("LeftButtonPressEvent", self.left_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_release)
    
    def left_press(self, obj, event):
        self.StartPan()
    
    def left_release(self, obj, event):
        self.EndPan()


def create_radar_image_actor(radar_data):
    """
    Create VTK image actor from radar grid data.
    Uses RGBA precip type colors if available, otherwise falls back to reflectivity.
    """
    if radar_data.get('rgba') is not None:
        return create_rgba_actor(radar_data)
    else:
        return create_reflectivity_actor(radar_data)


def create_rgba_actor(radar_data):
    """Create actor from pre-computed RGBA grid."""
    rgba = radar_data['rgba']
    ny, nx, _ = rgba.shape
    
    image = vtkImageData()
    image.SetDimensions(nx, ny, 1)
    image.SetSpacing(
        (radar_data['x_max'] - radar_data['x_min']) / nx,
        (radar_data['y_max'] - radar_data['y_min']) / ny,
        1.0
    )
    image.SetOrigin(radar_data['x_min'], radar_data['y_min'], 0)
    
    colors = vtkUnsignedCharArray()
    colors.SetNumberOfComponents(4)
    colors.SetNumberOfTuples(nx * ny)
    colors.SetName("RGBA")
    
    for j in range(ny):
        for i in range(nx):
            idx = j * nx + i
            colors.SetTuple4(
                idx,
                int(rgba[j, i, 0]),
                int(rgba[j, i, 1]),
                int(rgba[j, i, 2]),
                int(rgba[j, i, 3])
            )
    
    image.GetPointData().SetScalars(colors)
    
    mapper = vtkImageSliceMapper()
    mapper.SetInputData(image)
    mapper.BorderOn()
    
    actor = vtkImageSlice()
    actor.SetMapper(mapper)
    
    return actor


def create_reflectivity_actor(radar_data):
    """Fallback: create actor from reflectivity with standard colors."""
    from vtkmodules.vtkCommonCore import vtkLookupTable
    from vtkmodules.vtkRenderingCore import vtkImageProperty
    
    grid = radar_data['grid']
    ny, nx = grid.shape
    
    image = vtkImageData()
    image.SetDimensions(nx, ny, 1)
    image.SetSpacing(
        (radar_data['x_max'] - radar_data['x_min']) / nx,
        (radar_data['y_max'] - radar_data['y_min']) / ny,
        1.0
    )
    image.SetOrigin(radar_data['x_min'], radar_data['y_min'], 0)
    
    image.AllocateScalars(10, 1)
    
    for j in range(ny):
        for i in range(nx):
            val = grid[j, i]
            if np.isnan(val):
                val = -999
            image.SetScalarComponentFromFloat(i, j, 0, 0, val)
    
    lut = create_radar_lut()
    
    mapper = vtkImageSliceMapper()
    mapper.SetInputData(image)
    mapper.BorderOn()
    
    prop = vtkImageProperty()
    prop.SetLookupTable(lut)
    prop.SetColorWindow(105)
    prop.SetColorLevel(22.5)
    prop.SetInterpolationTypeToLinear()
    prop.UseLookupTableScalarRangeOn()
    
    actor = vtkImageSlice()
    actor.SetMapper(mapper)
    actor.SetProperty(prop)
    
    return actor


def create_radar_lut():
    """Create lookup table for reflectivity-only rendering."""
    from vtkmodules.vtkCommonCore import vtkLookupTable
    
    lut = vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetRange(-30, 75)
    
    color_stops = [
        (-30, 0, 0, 0),
        (-10, 0, 0, 0),
        (5, 0, 0.93, 0.93),
        (10, 0, 0.63, 0.93),
        (15, 0, 0, 0.93),
        (20, 0, 1, 0),
        (25, 0, 0.78, 0),
        (30, 0, 0.56, 0),
        (35, 1, 1, 0),
        (40, 1, 0.78, 0),
        (45, 1, 0.5, 0),
        (50, 1, 0, 0),
        (55, 0.78, 0, 0),
        (60, 0.56, 0, 0),
        (65, 1, 0, 1),
        (70, 0.6, 0, 0.6),
        (75, 1, 1, 1),
    ]
    
    lut.Build()
    
    for i in range(256):
        dbz = -30 + (105 * i / 255)
        
        r, g, b = 0, 0, 0
        for j in range(len(color_stops) - 1):
            if color_stops[j][0] <= dbz < color_stops[j+1][0]:
                t = (dbz - color_stops[j][0]) / (color_stops[j+1][0] - color_stops[j][0])
                r = color_stops[j][1] + t * (color_stops[j+1][1] - color_stops[j][1])
                g = color_stops[j][2] + t * (color_stops[j+1][2] - color_stops[j][2])
                b = color_stops[j][3] + t * (color_stops[j+1][3] - color_stops[j][3])
                break
        
        alpha = 0.0 if dbz < 15 else 0.85
        lut.SetTableValue(i, r, g, b, alpha)
    
    return lut


def create_radar_renderer(radar_data):
    """Create complete renderer with radar and overlays."""
    from components.state_boundries import create_state_actor
    from components.map_overlays import create_city_actors
    
    renderer = vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.18)
    
    # Add radar layer
    radar_actor = create_radar_image_actor(radar_data)
    renderer.AddViewProp(radar_actor)
    
    # Add state boundaries
    all_states_actor, oregon_actor = create_state_actor("Oregon")
    if all_states_actor:
        renderer.AddActor(all_states_actor)
    if oregon_actor:
        renderer.AddActor(oregon_actor)
    
    # Add cities
    city_actors = create_city_actors()
    for actor in city_actors:
        renderer.AddActor(actor)
    
    # Set up camera
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, 0, 1000)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 1, 0)
    camera.ParallelProjectionOn()
    renderer.ResetCamera()
    camera.SetParallelScale(500)
    
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)
    
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    style = MapInteractorStyle()
    interactor.SetInteractorStyle(style)
    
    return renderer, render_window