"""
Test script to verify weather API module
"""

from api.weather import fetch_all_weather, group_forecast_by_date

# Portland, Oregon
LAT = 45.5152
LON = -122.6784

print("Fetching weather data...")
current, forecast = fetch_all_weather(LAT, LON)

print("\n" + "=" * 60)
print("CURRENT WEATHER (for Today page)")
print("=" * 60)
if current:
    for key, value in current.items():
        print(f"  {key}: {value}")
else:
    print("  ERROR: No data")

print("\n" + "=" * 60)
print("FORECAST PREVIEW (first 4 for Today page)")
print("=" * 60)
for item in forecast[:4]:
    print(f"  {item['time']}: {item['temp']}°F, {item['condition']}")

print("\n" + "=" * 60)
print("FULL FORECAST GROUPED (for Hourly page)")
print("=" * 60)
grouped = group_forecast_by_date(forecast)
for group in grouped:
    print(f"\n{group['date']}:")
    for hour in group["hours"]:
        print(f"  {hour['time']}: {hour['temp']}°F, {hour['condition']}, {hour['precip_chance']}% precip")

print("\n" + "=" * 60)
print("Data ready for app integration!")
print("=" * 60)