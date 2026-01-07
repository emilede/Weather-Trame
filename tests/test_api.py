"""
Test NOAA + OWM hybrid weather API
"""

from api.weather_noaa import fetch_all_weather, group_forecast_by_date, get_noaa_grid

# Portland, Oregon
LAT = 45.5152
LON = -122.6784

print("=" * 60)
print("Testing NOAA API")
print("=" * 60)

# Test grid lookup
print("\n1. NOAA GRID LOOKUP")
print("-" * 40)
grid = get_noaa_grid(LAT, LON)
if grid:
    print(f"  Grid ID: {grid['grid_id']}")
    print(f"  Grid X,Y: {grid['grid_x']}, {grid['grid_y']}")
    print(f"  Hourly URL: {grid['forecast_hourly_url']}")
else:
    print("  ERROR: Could not get grid info")

# Test full weather fetch
print("\n2. FULL WEATHER FETCH")
print("-" * 40)
current, hourly = fetch_all_weather(LAT, LON)

if current:
    print("\nCURRENT CONDITIONS:")
    for key, value in current.items():
        print(f"  {key}: {value}")
else:
    print("  ERROR: No current data")

print("\n3. HOURLY FORECAST (first 8 hours)")
print("-" * 40)
for item in hourly[:8]:
    print(f"  {item['time']}: {item['temp']}°F, {item['condition']}, {item['precip_chance']}% precip")

print(f"\n  ... {len(hourly)} total hours available")

print("\n4. GROUPED BY DATE")
print("-" * 40)
grouped = group_forecast_by_date(hourly)
for group in grouped[:3]:
    print(f"\n{group['date']}: {len(group['hours'])} periods")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)