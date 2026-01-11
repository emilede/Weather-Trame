"""
Radar VTK Visualization
Creates VTK actors from radar data - image-based rendering
"""

import numpy as np
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkImageSlice,
    vtkImageSliceMapper,
    vtkImageProperty,
)
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
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


def create_radar_lut():
    """
    Create lookup table with standard radar reflectivity colors.
    """
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


def create_radar_image_actor(radar_data):
    """
    Create VTK image actor from radar grid data.
    """
    grid = radar_data['grid']
    ny, nx = grid.shape
    
    # Create image data
    image = vtkImageData()
    image.SetDimensions(nx, ny, 1)
    image.SetSpacing(
        (radar_data['x_max'] - radar_data['x_min']) / nx,
        (radar_data['y_max'] - radar_data['y_min']) / ny,
        1.0
    )
    image.SetOrigin(radar_data['x_min'], radar_data['y_min'], 0)
    
    # Fill with data
    image.AllocateScalars(10, 1)  # VTK_FLOAT = 10
    
    for j in range(ny):
        for i in range(nx):
            val = grid[j, i]
            if np.isnan(val):
                val = -999  # Mark as no data
            image.SetScalarComponentFromFloat(i, j, 0, 0, val)
    
    # Create mapper
    mapper = vtkImageSliceMapper()
    mapper.SetInputData(image)
    mapper.BorderOn()
    
    # Create image property with LUT
    lut = create_radar_lut()
    
    prop = vtkImageProperty()
    prop.SetLookupTable(lut)
    prop.SetColorWindow(105)  # Range width (-30 to 75)
    prop.SetColorLevel(22.5)  # Center of range
    prop.SetInterpolationTypeToLinear()
    prop.UseLookupTableScalarRangeOn()
    
    # Create image slice actor
    actor = vtkImageSlice()
    actor.SetMapper(mapper)
    actor.SetProperty(prop)
    
    return actor, lut


def create_scalar_bar(lut):
    """Create a legend/scalar bar for dBZ values."""
    scalar_bar = vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("dBZ")
    scalar_bar.SetNumberOfLabels(6)
    scalar_bar.SetWidth(0.08)
    scalar_bar.SetHeight(0.6)
    scalar_bar.SetPosition(0.9, 0.2)
    return scalar_bar


def create_radar_renderer(radar_data):
    """
    Create complete renderer with radar visualization.
    """
    from components.state_boundries import create_state_actor
    
    renderer = vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.15)
    
    # Add radar image
    radar_actor, lut = create_radar_image_actor(radar_data)
    renderer.AddViewProp(radar_actor)
    
    # Add state boundaries
    all_states_actor, oregon_actor = create_state_actor("Oregon")
    if all_states_actor:
        renderer.AddActor(all_states_actor)
    if oregon_actor:
        renderer.AddActor(oregon_actor)
        
    # Set up camera for top-down 2D view
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, 0, 1000)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 1, 0)
    camera.ParallelProjectionOn()
    renderer.ResetCamera()
    camera.SetParallelScale(500)
    
    # Create render window
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)
    
    # Custom interactor
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    style = MapInteractorStyle()
    interactor.SetInteractorStyle(style)
    
    return renderer, render_window