"""
State Boundaries for Radar Overlay
Converts US state boundaries to VTK actors
"""

import numpy as np
import geopandas as gpd
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

# Grid center (Oregon-centered)
GRID_CENTER_LAT = 44.0
GRID_CENTER_LON = -120.5

# Approximate conversion factors at this latitude
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * np.cos(np.radians(GRID_CENTER_LAT))


def latlon_to_km(lat, lon):
    """Convert lat/lon to km offset from grid center."""
    x = (lon - GRID_CENTER_LON) * KM_PER_DEG_LON
    y = (lat - GRID_CENTER_LAT) * KM_PER_DEG_LAT
    return x, y


def create_state_actor(focus_state="Oregon", bounds_km=500):
    """
    Create VTK actor with US state boundaries.
    
    Args:
        focus_state: State to highlight (thicker line)
        bounds_km: Only include geometry within this distance from radar
    
    Returns:
        tuple (all_states_actor, focus_state_actor)
    """
    # Load US states from GeoJSON URL
    url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    
    try:
        states = gpd.read_file(url)
        print(f"Loaded {len(states)} states")
    except Exception as e:
        print(f"Error loading boundaries: {e}")
        return None, None
    
    # Create VTK structures for all states
    all_points = vtkPoints()
    all_lines = vtkCellArray()
    
    # Create VTK structures for focus state
    focus_points = vtkPoints()
    focus_lines = vtkCellArray()
    
    point_id_all = 0
    point_id_focus = 0
    
    for idx, row in states.iterrows():
        state_name = row.get('name', '')
        geometry = row.geometry
        
        is_focus = (state_name == focus_state)
        
        # Handle MultiPolygon and Polygon
        if geometry.geom_type == 'MultiPolygon':
            polygons = list(geometry.geoms)
        elif geometry.geom_type == 'Polygon':
            polygons = [geometry]
        else:
            continue
        
        for polygon in polygons:
            # Get exterior coordinates
            coords = list(polygon.exterior.coords)
            
            # Check if any point is within bounds
            in_bounds = False
            for lon, lat in coords:
                x, y = latlon_to_km(lat, lon)
                if abs(x) < bounds_km and abs(y) < bounds_km:
                    in_bounds = True
                    break
            
            if not in_bounds:
                continue
            
            # Add to appropriate VTK structure
            if is_focus:
                line = []
                for lon, lat in coords:
                    x, y = latlon_to_km(lat, lon)
                    focus_points.InsertNextPoint(x, y, -0.1)
                    line.append(point_id_focus)
                    point_id_focus += 1
                
                focus_lines.InsertNextCell(len(line))
                for pid in line:
                    focus_lines.InsertCellPoint(pid)
            else:
                line = []
                for lon, lat in coords:
                    x, y = latlon_to_km(lat, lon)
                    all_points.InsertNextPoint(x, y, -0.1)
                    line.append(point_id_all)
                    point_id_all += 1
                
                all_lines.InsertNextCell(len(line))
                for pid in line:
                    all_lines.InsertCellPoint(pid)
    
    # Create actor for all states (dimmer)
    all_polydata = vtkPolyData()
    all_polydata.SetPoints(all_points)
    all_polydata.SetLines(all_lines)
    
    all_mapper = vtkPolyDataMapper()
    all_mapper.SetInputData(all_polydata)
    
    all_actor = vtkActor()
    all_actor.SetMapper(all_mapper)
    all_actor.GetProperty().SetColor(0.4, 0.4, 0.4)
    all_actor.GetProperty().SetLineWidth(1)
    
    # Create actor for focus state (brighter, thicker)
    focus_polydata = vtkPolyData()
    focus_polydata.SetPoints(focus_points)
    focus_polydata.SetLines(focus_lines)
    
    focus_mapper = vtkPolyDataMapper()
    focus_mapper.SetInputData(focus_polydata)
    
    focus_actor = vtkActor()
    focus_actor.SetMapper(focus_mapper)
    focus_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    focus_actor.GetProperty().SetLineWidth(2)
    
    print(f"All states points: {all_points.GetNumberOfPoints()}")
    print(f"Oregon points: {focus_points.GetNumberOfPoints()}")
    
    return all_actor, focus_actor


# Quick test
if __name__ == "__main__":
    print("Creating state boundary actors...")
    all_actor, focus_actor = create_state_actor("Oregon")
    if all_actor and focus_actor:
        print("Success!")
    else:
        print("Failed")
