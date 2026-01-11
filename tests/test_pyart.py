# tests/test_pyart.py
import pyart

filepath = "data/KRTX20260107_000524_V06.ar2v"

print("Loading radar file...")
radar = pyart.io.read_nexrad_archive(filepath)

print(f"Station: {radar.metadata['instrument_name']}")
print(f"Sweeps: {radar.nsweeps}")
print(f"Rays: {radar.nrays}")
print(f"Gates: {radar.ngates}")
print(f"Fields: {list(radar.fields.keys())}")
