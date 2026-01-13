"""
Precipitation Type Classifier
Uses radar reflectivity + temperature to classify precip type
"""

import numpy as np

# Precipitation type codes
PRECIP_NONE = 0
PRECIP_RAIN = 1
PRECIP_SNOW = 2
PRECIP_MIX = 3
PRECIP_FREEZING_RAIN = 4


def classify_precip_type(reflectivity, temp_2m, temp_850):
    """
    Classify precipitation type at each grid cell.
    """
    precip_type = np.full(reflectivity.shape, PRECIP_NONE, dtype=np.int8)
    
    has_precip = reflectivity > 5
    
    temp_2m = np.nan_to_num(temp_2m, nan=40)
    temp_850 = np.nan_to_num(temp_850, nan=40)
    
    rain_mask = has_precip & (temp_2m > 35)
    precip_type[rain_mask] = PRECIP_RAIN
    
    snow_mask = has_precip & (temp_2m < 28)
    precip_type[snow_mask] = PRECIP_SNOW
    
    mix_mask = has_precip & (temp_2m >= 28) & (temp_2m <= 35)
    precip_type[mix_mask] = PRECIP_MIX
    
    freezing_rain_mask = has_precip & (temp_850 > 32) & (temp_2m < 32)
    precip_type[freezing_rain_mask] = PRECIP_FREEZING_RAIN
    
    return precip_type


def get_precip_type_colors():
    """Return color mapping for each precip type."""
    return {
        PRECIP_NONE: (0, 0, 0, 0),
        PRECIP_RAIN: {
            'light': (0, 1, 0),
            'moderate': (1, 1, 0),
            'heavy': (1, 0, 0),
        },
        PRECIP_SNOW: {
            'light': (0.68, 0.85, 0.9),
            'moderate': (0.25, 0.41, 0.88),
            'heavy': (0.1, 0.1, 0.6),
        },
        PRECIP_MIX: {
            'light': (0.25, 0.88, 0.82),
            'moderate': (0, 0.55, 0.55),
            'heavy': (0, 0.39, 0.39),
        },
        PRECIP_FREEZING_RAIN: {
            'light': (1, 0.41, 0.71),
            'moderate': (0.78, 0.08, 0.52),
            'heavy': (0.55, 0, 0.35),
        },
    }


def get_intensity_level(dbz):
    """Convert dBZ to intensity level."""
    if dbz < 20:
        return 'light'
    elif dbz < 40:
        return 'moderate'
    else:
        return 'heavy'


def create_rgba_grid(reflectivity, precip_type):
    """
    Create RGBA color grid based on precip type and intensity.
    """
    ny, nx = reflectivity.shape
    rgba = np.zeros((ny, nx, 4), dtype=np.uint8)
    
    colors = get_precip_type_colors()
    
    for ptype in [PRECIP_RAIN, PRECIP_SNOW, PRECIP_MIX, PRECIP_FREEZING_RAIN]:
        mask = precip_type == ptype
        
        if not np.any(mask):
            continue
        
        indices = np.where(mask)
        
        for i, j in zip(indices[0], indices[1]):
            dbz = reflectivity[i, j]
            intensity = get_intensity_level(dbz)
            color = colors[ptype][intensity]
            
            rgba[i, j, 0] = int(color[0] * 255)
            rgba[i, j, 1] = int(color[1] * 255)
            rgba[i, j, 2] = int(color[2] * 255)
            
            if dbz < 10:
                rgba[i, j, 3] = 100
            elif dbz < 30:
                rgba[i, j, 3] = 180
            else:
                rgba[i, j, 3] = 220
    
    return rgba


if __name__ == "__main__":
    ny, nx = 100, 100
    
    reflectivity = np.zeros((ny, nx))
    reflectivity[30:70, 30:70] = 25
    reflectivity[40:60, 40:60] = 45
    
    temp_2m = np.linspace(20, 50, ny).reshape(-1, 1) * np.ones((1, nx))
    temp_850 = temp_2m + 10
    
    precip_type = classify_precip_type(reflectivity, temp_2m, temp_850)
    
    print("Precip type distribution:")
    for ptype, name in [(0, "None"), (1, "Rain"), (2, "Snow"), (3, "Mix"), (4, "Frz Rain")]:
        count = np.sum(precip_type == ptype)
        print(f"  {name}: {count} cells")
    
    rgba = create_rgba_grid(reflectivity, precip_type)
    print(f"\nRGBA grid shape: {rgba.shape}")
    print(f"Non-transparent pixels: {np.sum(rgba[:,:,3] > 0)}")

