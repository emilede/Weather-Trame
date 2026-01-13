"""
HRRR Model Data Fetcher
Fetches temperature data for precipitation type classification
"""

import numpy as np
from datetime import datetime, timedelta

# Oregon region bounds (matches radar grid)
GRID_CENTER_LAT = 44.0
GRID_CENTER_LON = -120.5
GRID_LIMITS_KM = 500

# Lat/lon bounds for subsetting HRRR
LAT_MIN = 39.5
LAT_MAX = 48.5
LON_MIN = -125.5
LON_MAX = -115.5


def get_latest_hrrr_temps():
    """
    Fetch latest HRRR temperature data.
    
    Returns:
        dict with 'temp_2m', 'temp_850mb', 'lats', 'lons' arrays
        or None on error
    """
    from herbie import Herbie
    
    now = datetime.utcnow()
    
    for hours_back in range(0, 6):
        run_time = now - timedelta(hours=hours_back)
        run_time = run_time.replace(minute=0, second=0, microsecond=0)
        
        try:
            print(f"Trying HRRR run: {run_time.strftime('%Y-%m-%d %H:%M')} UTC")
            
            H = Herbie(
                run_time,
                model="hrrr",
                product="sfc",
                fxx=0,
            )
            
            ds_2m = H.xarray(":TMP:2 m above ground")
            
            H_prs = Herbie(
                run_time,
                model="hrrr",
                product="prs",
                fxx=0,
            )
            ds_850 = H_prs.xarray(":TMP:850 mb")
            
            temp_2m = ds_2m['t2m'].values if 't2m' in ds_2m else ds_2m['TMP_2maboveground'].values
            lats = ds_2m['latitude'].values
            lons = ds_2m['longitude'].values
            
            if lons.max() > 180:
                lons = np.where(lons > 180, lons - 360, lons)
            
            temp_850 = ds_850['t'].values if 't' in ds_850 else ds_850['TMP_850mb'].values
            
            lat_mask = (lats >= LAT_MIN) & (lats <= LAT_MAX)
            lon_mask = (lons >= LON_MIN) & (lons <= LON_MAX)
            
            if lats.ndim == 1:
                lat_idx = np.where(lat_mask)[0]
                lon_idx = np.where(lon_mask)[0]
                temp_2m = temp_2m[lat_idx[0]:lat_idx[-1]+1, lon_idx[0]:lon_idx[-1]+1]
                temp_850 = temp_850[lat_idx[0]:lat_idx[-1]+1, lon_idx[0]:lon_idx[-1]+1]
                lats = lats[lat_idx[0]:lat_idx[-1]+1]
                lons = lons[lon_idx[0]:lon_idx[-1]+1]
            
            temp_2m_f = (temp_2m - 273.15) * 9/5 + 32
            temp_850_f = (temp_850 - 273.15) * 9/5 + 32
            
            print(f"HRRR data loaded: {temp_2m_f.shape}")
            print(f"2m temp range: {temp_2m_f.min():.1f}°F to {temp_2m_f.max():.1f}°F")
            
            return {
                'temp_2m': temp_2m_f,
                'temp_850': temp_850_f,
                'lats': lats,
                'lons': lons,
                'time': run_time,
            }
            
        except Exception as e:
            print(f"Failed for {run_time}: {e}")
            continue
    
    print("Could not fetch HRRR data")
    return None


def regrid_to_radar(hrrr_data, radar_grid_shape, radar_bounds):
    """
    Interpolate HRRR data to match radar grid.
    """
    from scipy.interpolate import griddata
    
    ny, nx = radar_grid_shape
    
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * np.cos(np.radians(GRID_CENTER_LAT))
    
    lat_min = GRID_CENTER_LAT + radar_bounds['y_min'] / km_per_deg_lat
    lat_max = GRID_CENTER_LAT + radar_bounds['y_max'] / km_per_deg_lat
    lon_min = GRID_CENTER_LON + radar_bounds['x_min'] / km_per_deg_lon
    lon_max = GRID_CENTER_LON + radar_bounds['x_max'] / km_per_deg_lon
    
    radar_lats = np.linspace(lat_min, lat_max, ny)
    radar_lons = np.linspace(lon_min, lon_max, nx)
    radar_lon_grid, radar_lat_grid = np.meshgrid(radar_lons, radar_lats)
    
    hrrr_lats = hrrr_data['lats']
    hrrr_lons = hrrr_data['lons']
    
    # Handle both 1D and 2D lat/lon arrays
    if hrrr_lats.ndim == 1:
        hrrr_lon_grid, hrrr_lat_grid = np.meshgrid(hrrr_lons, hrrr_lats)
    else:
        hrrr_lat_grid = hrrr_lats
        hrrr_lon_grid = hrrr_lons
    
    # Flatten source points
    points = np.column_stack([hrrr_lat_grid.ravel(), hrrr_lon_grid.ravel()])
    
    # Flatten target points
    target_points = np.column_stack([radar_lat_grid.ravel(), radar_lon_grid.ravel()])
    
    # Interpolate
    temp_2m_regrid = griddata(
        points,
        hrrr_data['temp_2m'].ravel(),
        target_points,
        method='linear',
        fill_value=np.nan,
    ).reshape(ny, nx)
    
    temp_850_regrid = griddata(
        points,
        hrrr_data['temp_850'].ravel(),
        target_points,
        method='linear',
        fill_value=np.nan,
    ).reshape(ny, nx)
    
    return {
        'temp_2m': temp_2m_regrid,
        'temp_850': temp_850_regrid,
    }


if __name__ == "__main__":
    print("Fetching HRRR temperature data...")
    data = get_latest_hrrr_temps()
    if data:
        print(f"\nSuccess!")
        print(f"Time: {data['time']}")
        print(f"Grid shape: {data['temp_2m'].shape}")
    else:
        print("Failed")