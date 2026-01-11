"""
Radar Data Processor
Converts NEXRAD data to VTK-ready arrays
Supports single station and multi-station composites
"""

import numpy as np
import pyart


def load_radar(filepath):
    """Load a NEXRAD file with PyART."""
    return pyart.io.read_nexrad_archive(filepath)


def extract_sweep(radar, sweep=0, field='reflectivity'):
    """
    Extract a single sweep and convert to cartesian coordinates.
    """
    start = radar.sweep_start_ray_index['data'][sweep]
    end = radar.sweep_end_ray_index['data'][sweep]
    
    azimuths = radar.azimuth['data'][start:end+1]
    ranges = radar.range['data']
    data = radar.fields[field]['data'][start:end+1]
    
    if hasattr(data, 'filled'):
        data = data.filled(np.nan)
    
    az_rad = np.deg2rad(90 - azimuths)
    r, theta = np.meshgrid(ranges, az_rad)
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    x_flat = x.flatten()
    y_flat = y.flatten()
    values_flat = data.flatten()
    
    valid = ~np.isnan(values_flat)
    x_flat = x_flat[valid]
    y_flat = y_flat[valid]
    values_flat = values_flat[valid]
    
    elevation = radar.fixed_angle['data'][sweep]
    scan_time = pyart.util.datetime_from_radar(radar)
    
    return {
        'x': x_flat,
        'y': y_flat,
        'values': values_flat,
        'elevation': elevation,
        'time': scan_time,
        'field': field,
        'num_points': len(x_flat),
        'range_max': ranges.max(),
    }


def get_reflectivity_for_vtk(filepath, sweep=0):
    """
    Main function: load file and get VTK-ready data.
    """
    radar = load_radar(filepath)
    return extract_sweep(radar, sweep=sweep, field='reflectivity')


def create_composite(radar_files, grid_shape=(800, 800), grid_limits_km=500):
    """
    Create a composite from multiple radar files.
    
    Args:
        radar_files: Dict of {station: filepath}
        grid_shape: (ny, nx) grid dimensions
        grid_limits_km: Half-width of grid in km (500 = 1000km total)
    
    Returns:
        Dict with lat, lon, values arrays and metadata
    """
    # Load all radars
    radars = []
    for station, filepath in radar_files.items():
        print(f"Loading {station}...")
        radar = load_radar(filepath)
        radars.append(radar)
    
    if not radars:
        return None
    
    # Oregon-centered grid (roughly centered on state)
    # Oregon center is approximately 43.8°N, -120.5°W
    grid_center_lat = 44.0
    grid_center_lon = -120.5
    
    # Convert km to meters for PyART
    grid_limits_m = grid_limits_km * 1000
    
    print(f"Creating composite grid ({grid_shape[0]}x{grid_shape[1]})...")
    
    try:
        # Create grid from all radars
        grid = pyart.map.grid_from_radars(
            radars,
            grid_shape=(1, grid_shape[0], grid_shape[1]),  # (nz, ny, nx)
            grid_limits=(
                (0, 1000),  # z limits (meters) - just surface level
                (-grid_limits_m, grid_limits_m),  # y limits
                (-grid_limits_m, grid_limits_m),  # x limits
            ),
            grid_origin=(grid_center_lat, grid_center_lon),
            grid_projection={
                'proj': 'lcc',
                'lat_0': grid_center_lat,
                'lon_0': grid_center_lon,
                'lat_1': grid_center_lat - 5,
                'lat_2': grid_center_lat + 5,
            },
            fields=['reflectivity'],
            weighting_function='nearest',
            roi_func='constant',
            constant_roi=2000,  # 2km radius of influence
        )
        
        # Extract data
        reflectivity = grid.fields['reflectivity']['data'][0]  # First (only) z level
        
        if hasattr(reflectivity, 'filled'):
            reflectivity = reflectivity.filled(np.nan)
        
        # Get lat/lon coordinates
        lons = grid.x['data'] / 1000  # Convert to km for display
        lats = grid.y['data'] / 1000
        
        # Create meshgrid
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        
        # Flatten for VTK
        x_flat = lon_grid.flatten()
        y_flat = lat_grid.flatten()
        values_flat = reflectivity.flatten()
        
        # Remove NaN
        valid = ~np.isnan(values_flat)
        x_flat = x_flat[valid]
        y_flat = y_flat[valid]
        values_flat = values_flat[valid]
        
        # Get most recent scan time
        scan_time = pyart.util.datetime_from_radar(radars[0])
        
        print(f"Composite created: {len(x_flat):,} points")
        
        return {
            'x': x_flat * 1000,  # Convert back to meters for consistency
            'y': y_flat * 1000,
            'values': values_flat,
            'time': scan_time,
            'num_points': len(x_flat),
            'grid_center': (grid_center_lat, grid_center_lon),
            'stations': list(radar_files.keys()),
        }
        
    except Exception as e:
        print(f"Error creating composite: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def create_composite_grid(radar_files, grid_shape=(800, 800), grid_limits_km=500):
    """
    Create a composite that returns a 2D grid (not flattened).
    For smooth image rendering.
    """
    radars = []
    for station, filepath in radar_files.items():
        print(f"Loading {station}...")
        radar = load_radar(filepath)
        radars.append(radar)
    
    if not radars:
        return None
    
    grid_center_lat = 44.0
    grid_center_lon = -120.5
    grid_limits_m = grid_limits_km * 1000
    
    print(f"Creating composite grid ({grid_shape[0]}x{grid_shape[1]})...")
    
    try:
        grid = pyart.map.grid_from_radars(
            radars,
            grid_shape=(1, grid_shape[0], grid_shape[1]),
            grid_limits=(
                (0, 1000),
                (-grid_limits_m, grid_limits_m),
                (-grid_limits_m, grid_limits_m),
            ),
            grid_origin=(grid_center_lat, grid_center_lon),
            grid_projection={
                'proj': 'lcc',
                'lat_0': grid_center_lat,
                'lon_0': grid_center_lon,
                'lat_1': grid_center_lat - 5,
                'lat_2': grid_center_lat + 5,
            },
            fields=['reflectivity'],
            weighting_function='nearest',
            roi_func='constant',
            constant_roi=2000,
        )
        
        reflectivity = grid.fields['reflectivity']['data'][0]
        
        if hasattr(reflectivity, 'filled'):
            reflectivity = reflectivity.filled(np.nan)
        
        scan_time = pyart.util.datetime_from_radar(radars[0])
        
        print(f"Composite grid created: {grid_shape[0]}x{grid_shape[1]}")
        
        return {
            'grid': reflectivity,
            'x_min': -grid_limits_km,
            'x_max': grid_limits_km,
            'y_min': -grid_limits_km,
            'y_max': grid_limits_km,
            'time': scan_time,
            'grid_center': (grid_center_lat, grid_center_lon),
            'stations': list(radar_files.keys()),
        }
        
    except Exception as e:
        print(f"Error creating composite: {e}")
        import traceback
        traceback.print_exc()
        return None


# Quick test
if __name__ == "__main__":
    import os
    
    # Test single file
    data_dir = "data"
    files = [f for f in os.listdir(data_dir) if f.startswith('KRTX') and '_V06' in f]
    if files:
        filepath = os.path.join(data_dir, sorted(files)[-1])
        print(f"Testing single file: {filepath}")
        data = get_reflectivity_for_vtk(filepath)
        print(f"Single station: {data['num_points']:,} points")
    
    # Test composite
    print("\n--- Testing Composite ---")
    from api.nexrad import get_oregon_radars
    radar_files = get_oregon_radars()
    if radar_files:
        composite = create_composite(radar_files)
        if composite:
            print(f"Composite: {composite['num_points']:,} points")
            print(f"Stations: {composite['stations']}")