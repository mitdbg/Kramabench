#!/usr/bin/env python
# coding: utf-8


# Q5

import numpy as np
from datetime import timedelta
from skyfield.api import load, EarthSatellite

def read_tle_file(filename):
    """Reads a TLE file and returns a list of (line1, line2) tuples."""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) % 2 != 0:
        raise ValueError("TLE file should contain an even number of lines.")
    return [(lines[i], lines[i+1]) for i in range(0, len(lines), 2)]


from skyfield.api import load, wgs84, EarthSatellite  # type: ignore

ts = load.timescale()

def calculate_orbit_with_tle(satellite):
    """
    calculate the height of a satellite based on tle
    Returns:
        height in km
    """
    #code based off of https://rhodesmill.org/skyfield/earth-satellites.html
    gcrsLocation = satellite.at(ts.utc(satellite.epoch.utc_datetime()))
    itrs = gcrsLocation.itrf_xyz().m
    loc = (itrs[0], itrs[1], itrs[2])
    return sum([i**2 for i in loc]) ** (1/2) / 1000

def detect_altitude_change(tle_pairs, threshold_km=0.1, t_hours=12):
    """
    Detects altitude_change based on changes in estimated height within a specified time window.
    
    Parameters:
    - tle_pairs: List of TLE line pairs.
    - threshold_km: Threshold for detecting altitude change in kilometers.
    - t_hours: Time window in hours to consider for maneuver detection.
    
    Returns:
    - List of tuples containing the epoch and delta_a where altitude change are detected.
    """
    ts = load.timescale()
    sat_height = []
    epochs = []

    for line1, line2 in tle_pairs:
        satellite = EarthSatellite(line1, line2, ts=ts)
        a = calculate_orbit_with_tle(satellite)
        sat_height.append(a)
        epochs.append(satellite.epoch.utc_datetime())

    altitude_change = []
    for i in range(1, len(sat_height)):
        delta_a = abs(sat_height[i] - sat_height[i - 1])
        delta_t = (epochs[i] - epochs[i - 1]).total_seconds() / 3600.0  # Convert to hours
        if delta_a > threshold_km and delta_t <= t_hours:
            altitude_change.append((delta_a, epochs[i-1], epochs[i]))

    return altitude_change, sat_height


tle_filename = './data/astronomy/input/TLE/48445.tle'  # Replace with your TLE file path
threshold_km = 1  # Threshold for detecting altitude_change in kilometers
hour_interval = 12

try:
    tle_pairs = read_tle_file(tle_filename)
except Exception as e:
    print(f"Error reading TLE file: {e}")

altitude_change, sat_height = detect_altitude_change(tle_pairs, threshold_km, hour_interval)
print(f"Maximum altitude change: {max([d[0] for d in altitude_change])}")

print(f"Total altitude_change detected: {len(altitude_change)}")
for delta_a, epoch0, epoch1 in altitude_change:
    print(f"Maneuver detected {epoch0}-{epoch1} with delta_a = {delta_a:.3f} km")



