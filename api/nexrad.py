"""
NEXRAD Level 2 Data Fetcher
Uses nexradaws library
"""

import os
from datetime import datetime, timedelta
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Oregon-area NEXRAD stations
OREGON_STATIONS = ["KRTX", "KPDT", "KMAX", "KLGX"]


def get_latest_radar(station="KRTX"):
    """
    Get the most recent radar file for a station.
    
    Returns:
        Local file path or None
    """
    import nexradaws
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = nexradaws.NexradAwsInterface()
    
    end = pd.Timestamp.utcnow()
    start = end - pd.Timedelta(hours=2)
    
    print(f"Searching for {station} scans from {start} to {end}...")
    
    try:
        scans = conn.get_avail_scans_in_range(start, end, station)
        
        if not scans:
            print(f"No scans found for {station} in last 2 hours, trying last 24 hours...")
            start = end - pd.Timedelta(hours=24)
            scans = conn.get_avail_scans_in_range(start, end, station)
        
        if not scans:
            print(f"No scans found for {station}")
            return None
        
        print(f"Found {len(scans)} scans for {station}")
        
        for scan in reversed(scans):
            if not scan.filename.endswith("MDM"):
                local_path = os.path.join(DATA_DIR, scan.filename)
                if os.path.exists(local_path):
                    print(f"Using cached: {scan.filename}")
                    return local_path
                
                print(f"Downloading: {scan.filename}")
                results = conn.download(scan, DATA_DIR)
                
                if results.success:
                    downloaded = results.success[0]
                    print(f"Saved: {downloaded.filepath}")
                    return downloaded.filepath
                else:
                    print("Download failed")
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_oregon_radars():
    """
    Get the most recent radar file from each Oregon-area station.
    
    Returns:
        Dict of {station: filepath} for successful downloads
    """
    radar_files = {}
    
    for station in OREGON_STATIONS:
        print(f"\n--- Fetching {station} ---")
        filepath = get_latest_radar(station)
        if filepath:
            radar_files[station] = filepath
        else:
            print(f"Warning: Could not get data for {station}")
    
    print(f"\nSuccessfully loaded {len(radar_files)}/{len(OREGON_STATIONS)} stations")
    return radar_files


def get_radar_sequence(station="KRTX", count=6):
    """
    Get a sequence of recent radar files for animation.
    
    Returns:
        List of local file paths
    """
    import nexradaws
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = nexradaws.NexradAwsInterface()
    
    end = pd.Timestamp.utcnow()
    start = end - pd.Timedelta(hours=2)
    
    try:
        scans = conn.get_avail_scans_in_range(start, end, station)
        
        if not scans:
            return []
        
        valid_scans = [s for s in scans if not s.filename.endswith("MDM")]
        recent = valid_scans[-count:]
        
        paths = []
        for scan in recent:
            local_path = os.path.join(DATA_DIR, scan.filename)
            
            if os.path.exists(local_path):
                print(f"Using cached: {scan.filename}")
                paths.append(local_path)
            else:
                print(f"Downloading: {scan.filename}")
                results = conn.download(scan, DATA_DIR)
                if results.success:
                    paths.append(results.success[0].filepath)
        
        return paths
        
    except Exception as e:
        print(f"Error: {e}")
        return []


# Quick test
if __name__ == "__main__":
    print("Fetching Oregon radar stations...")
    print("(This takes ~30 seconds per station due to PyART import)")
    files = get_oregon_radars()
    print(f"\nResults: {files}")

