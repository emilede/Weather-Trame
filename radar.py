"""
NEXRAD Radar Visualization using VTK
Fetches radar data and renders using VTK pipeline in Trame
"""

import requests
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta, timezone
from PIL import Image

from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkImageActor,
    vtkImageMapper3D,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.util.numpy_support import numpy_to_vtk

# Required for rendering
import vtkmodules.vtkRenderingOpenGL2  # noqa


# Iowa State Mesonet WMS for NEXRAD composites
MESONET_WMS = "https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi"

# Pacific Northwest bounds (Oregon + surroundings)
PNW_BOUNDS = {
    "west": -126.0,
    "east": -116.0,
    "south": 41.5,
    "north": 47.0,
}

# Image dimensions
IMG_WIDTH = 800
IMG_HEIGHT = 600


def get_radar_timestamps(count=12):
    """
    Get list of recent radar timestamps (5-min intervals).
    Returns list of datetime objects, oldest first.
    """
    now = datetime.now(timezone.utc)
    minutes = (now.minute // 5) * 5
    base_time = now.replace(minute=minutes, second=0, microsecond=0)
    
    timestamps = []
    for i in range(count):
        t = base_time - timedelta(minutes=i * 5)
        timestamps.append(t)
    
    return list(reversed(timestamps))


def build_wms_url(timestamp=None, bounds=None):
    """Build WMS URL for radar image."""
    if bounds is None:
        bounds = PNW_BOUNDS
    
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "nexrad-n0r-wmst",
        "WIDTH": IMG_WIDTH,
        "HEIGHT": IMG_HEIGHT,
        "SRS": "EPSG:4326",
        "BBOX": f"{bounds['west']},{bounds['south']},{bounds['east']},{bounds['north']}",
    }
    
    if timestamp:
        params["TIME"] = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{MESONET_WMS}?{query}"


def fetch_radar_image(timestamp=None, bounds=None):
    """
    Fetch radar image and return as numpy array.
    Returns RGBA numpy array (height, width, 4) or None on error.
    """
    url = build_wms_url(timestamp, bounds)
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Load image with PIL
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGBA")
        
        # Convert to numpy array
        arr = np.array(img)
        
        return arr
    except Exception as e:
        print(f"Error fetching radar image: {e}")
        return None


def numpy_to_vtk_image(np_array):
    """
    Convert numpy RGBA array to vtkImageData.
    
    Args:
        np_array: numpy array of shape (height, width, 4) with RGBA values
    
    Returns:
        vtkImageData object
    """
    if np_array is None:
        return None
    
    height, width, channels = np_array.shape
    
    # VTK expects data in (x, y) order, numpy is (row, col)
    # Flip vertically because VTK origin is bottom-left
    np_array = np.flipud(np_array)
    
    # Flatten to 1D array (VTK format)
    flat = np_array.reshape(-1, channels)
    
    # Create VTK array
    vtk_arr = numpy_to_vtk(flat, deep=True)
    vtk_arr.SetNumberOfComponents(channels)
    
    # Create vtkImageData
    image_data = vtkImageData()
    image_data.SetDimensions(width, height, 1)
    image_data.SetSpacing(1.0, 1.0, 1.0)
    image_data.SetOrigin(0.0, 0.0, 0.0)
    image_data.GetPointData().SetScalars(vtk_arr)
    
    return image_data


def create_radar_renderer():
    """
    Create VTK renderer with radar visualization pipeline.
    Returns (renderer, render_window, image_actor) tuple.
    """
    # Create renderer
    renderer = vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.15)  # Dark background
    
    # Create render window
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(IMG_WIDTH, IMG_HEIGHT)
    render_window.SetOffScreenRendering(1)  # For server-side rendering
    
    # Create image actor (will be updated with radar data)
    image_actor = vtkImageActor()
    renderer.AddActor(image_actor)
    
    return renderer, render_window, image_actor


def update_radar_image(image_actor, renderer, timestamp=None):
    """
    Fetch new radar data and update the VTK image actor.
    
    Args:
        image_actor: vtkImageActor to update
        renderer: vtkRenderer for camera reset
        timestamp: datetime for specific time, or None for latest
    
    Returns:
        True if successful, False otherwise
    """
    # Fetch radar image
    np_image = fetch_radar_image(timestamp)
    if np_image is None:
        return False
    
    # Convert to VTK
    vtk_image = numpy_to_vtk_image(np_image)
    if vtk_image is None:
        return False
    
    # Update actor
    image_actor.GetMapper().SetInputData(vtk_image)
    
    # Reset camera to fit image
    renderer.ResetCamera()
    
    return True


class RadarVisualization:
    """
    Manages radar visualization state and VTK pipeline.
    """
    
    def __init__(self):
        self.renderer, self.render_window, self.image_actor = create_radar_renderer()
        self.timestamps = []
        self.current_index = 0
        self.bounds = PNW_BOUNDS.copy()
    
    def load_timestamps(self, count=12):
        """Load available radar timestamps."""
        self.timestamps = get_radar_timestamps(count)
        self.current_index = len(self.timestamps) - 1  # Start at latest
        return self.timestamps
    
    def update_frame(self, index=None):
        """Update to specific frame index or current."""
        if index is not None:
            self.current_index = max(0, min(index, len(self.timestamps) - 1))
        
        if not self.timestamps:
            return False
        
        timestamp = self.timestamps[self.current_index]
        return update_radar_image(self.image_actor, self.renderer, timestamp)
    
    def next_frame(self):
        """Advance to next frame."""
        if self.current_index < len(self.timestamps) - 1:
            self.current_index += 1
            return self.update_frame()
        return False
    
    def prev_frame(self):
        """Go to previous frame."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.update_frame()
        return False
    
    def get_current_time_str(self):
        """Get formatted string of current timestamp."""
        if not self.timestamps:
            return "No data"
        ts = self.timestamps[self.current_index]
        return ts.strftime("%I:%M %p UTC")
    
    def set_bounds(self, west, east, south, north):
        """Update geographic bounds for radar fetch."""
        self.bounds = {
            "west": west,
            "east": east,
            "south": south,
            "north": north,
        }