"""
NEXRAD Radar - Simple image URL builder
"""

from datetime import datetime, timezone

# Iowa State Mesonet WMS for NEXRAD composites
MESONET_WMS = "https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0q.cgi"

# Pacific Northwest bounds
PNW_BOUNDS = {
    "west": -126.0,
    "east": -116.0,
    "south": 41.5,
    "north": 47.0,
}


def get_radar_url(bounds=None, width=800, height=500):
    """Build WMS URL for radar image."""
    if bounds is None:
        bounds = PNW_BOUNDS
    
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "nexrad-n0q",
        "WIDTH": width,
        "HEIGHT": height,
        "SRS": "EPSG:4326",
        "BBOX": f"{bounds['west']},{bounds['south']},{bounds['east']},{bounds['north']}",
    }
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{MESONET_WMS}?{query}"


def get_basemap_url(bounds=None, width=800, height=500):
    """Get OpenStreetMap WMS for basemap."""
    if bounds is None:
        bounds = PNW_BOUNDS
    
    # Use a simple basemap
    base = "https://mesonet.agron.iastate.edu/cgi-bin/wms/us/wwa.cgi"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "states",
        "WIDTH": width,
        "HEIGHT": height,
        "SRS": "EPSG:4326",
        "BBOX": f"{bounds['west']},{bounds['south']},{bounds['east']},{bounds['north']}",
    }
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base}?{query}"


def get_timestamp():
    """Get current UTC timestamp string."""
    return datetime.now(timezone.utc).strftime("%I:%M %p UTC")