"""
Map Overlays
City markers and highway lines for radar visualization
"""

import numpy as np
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor, vtkTextActor

# Grid center (must match radar_processor.py)
GRID_CENTER_LAT = 44.0
GRID_CENTER_LON = -120.5

KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * np.cos(np.radians(GRID_CENTER_LAT))

# Oregon cities
CITIES = [
    {"name": "Portland", "lat": 45.5152, "lon": -122.6784},
    {"name": "Salem", "lat": 44.9429, "lon": -123.0351},
    {"name": "Eugene", "lat": 44.0521, "lon": -123.0868},
    {"name": "Bend", "lat": 44.0582, "lon": -121.3153},
    {"name": "Medford", "lat": 42.3265, "lon": -122.8756},
    {"name": "Corvallis", "lat": 44.5646, "lon": -123.2620},
    {"name": "Astoria", "lat": 46.1879, "lon": -123.8313},
    {"name": "Pendleton", "lat": 45.6721, "lon": -118.7886},
    {"name": "Klamath Falls", "lat": 42.2249, "lon": -121.7817},
    {"name": "The Dalles", "lat": 45.5946, "lon": -121.1787},
    # Washington cities in view
    {"name": "Seattle", "lat": 47.6062, "lon": -122.3321},
    {"name": "Olympia", "lat": 47.0379, "lon": -122.9007},
    {"name": "Spokane", "lat": 47.6588, "lon": -117.4260},
    # California cities in view
    {"name": "Redding", "lat": 40.5865, "lon": -122.3917},
    # Idaho cities in view
    {"name": "Boise", "lat": 43.6150, "lon": -116.2023},
]

# Major highways (simplified paths)
HIGHWAYS = [
    {
        "name": "I-5",
        "color": (0.8, 0.4, 0.4),
        "points": [
            (42.0, -122.6), (42.5, -122.8), (43.0, -123.0), (43.5, -123.1),
            (44.0, -123.1), (44.5, -123.1), (45.0, -122.8), (45.5, -122.7),
            (46.0, -122.9), (46.5, -122.9), (47.0, -122.5), (47.5, -122.4),
        ]
    },
    {
        "name": "I-84",
        "color": (0.4, 0.6, 0.8),
        "points": [
            (45.5, -122.7), (45.6, -122.2), (45.6, -121.5), (45.6, -121.0),
            (45.7, -120.5), (45.7, -119.5), (45.7, -118.8), (45.7, -118.0),
            (45.5, -117.5), (44.5, -117.0), (44.0, -116.5), (43.6, -116.2),
        ]
    },
    {
        "name": "US-101",
        "color": (0.5, 0.7, 0.5),
        "points": [
            (42.0, -124.3), (42.5, -124.4), (43.0, -124.4), (43.5, -124.2),
            (44.0, -124.1), (44.5, -124.0), (45.0, -123.9), (45.5, -123.9),
            (46.0, -123.9), (46.2, -124.0), (46.5, -124.0), (47.0, -124.0),
        ]
    },
    {
        "name": "US-97",
        "color": (0.7, 0.6, 0.4),
        "points": [
            (42.2, -121.8), (42.5, -121.6), (43.0, -121.5), (43.5, -121.4),
            (44.0, -121.3), (44.5, -121.2), (45.0, -121.1), (45.5, -121.1),
        ]
    },
]


def latlon_to_km(lat, lon):
    """Convert lat/lon to km offset from grid center."""
    x = (lon - GRID_CENTER_LON) * KM_PER_DEG_LON
    y = (lat - GRID_CENTER_LAT) * KM_PER_DEG_LAT
    return x, y


def create_city_actors():
    """Create actors for city markers and labels."""
    actors = []
    
    for city in CITIES:
        x, y = latlon_to_km(city['lat'], city['lon'])
        
        # Skip if outside visible area
        if abs(x) > 550 or abs(y) > 550:
            continue
        
        # Create dot
        points = vtkPoints()
        points.InsertNextPoint(x, y, 2)
        
        vertices = vtkCellArray()
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(0)
        
        polydata = vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts(vertices)
        
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        dot_actor = vtkActor()
        dot_actor.SetMapper(mapper)
        dot_actor.GetProperty().SetColor(1, 1, 1)
        dot_actor.GetProperty().SetPointSize(6)
        actors.append(dot_actor)
        
        # Create label
        label = vtkTextActor()
        label.SetInput(city['name'])
        label.GetTextProperty().SetFontSize(12)
        label.GetTextProperty().SetColor(0.9, 0.9, 0.9)
        label.GetTextProperty().SetFontFamilyToArial()
        label.GetTextProperty().BoldOff()
        label.GetPositionCoordinate().SetCoordinateSystemToWorld()
        label.GetPositionCoordinate().SetValue(x + 8, y - 3, 2)
        actors.append(label)
    
    return actors


def create_highway_actors():
    """Create actors for highway lines."""
    actors = []
    
    for highway in HIGHWAYS:
        points = vtkPoints()
        lines = vtkCellArray()
        
        # Convert points to km
        km_points = []
        for lat, lon in highway['points']:
            x, y = latlon_to_km(lat, lon)
            km_points.append((x, y))
        
        # Add points
        for x, y in km_points:
            points.InsertNextPoint(x, y, 1)
        
        # Create line strip
        n_points = len(km_points)
        lines.InsertNextCell(n_points)
        for i in range(n_points):
            lines.InsertCellPoint(i)
        
        polydata = vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*highway['color'])
        actor.GetProperty().SetLineWidth(1.5)
        actor.GetProperty().SetOpacity(0.6)
        actors.append(actor)
    
    return actors

