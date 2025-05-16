#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os


file_path = './data/astronomy/input/SILSO/SN_y_tot_V2.0.csv' 

# --- Load Data ---
print(f"Attempting to load data from: {file_path}")

# Load CSV data - SILSO CSV files use semicolon (;) as delimiter
# Column names based on SILSO format: Year, Sunspot Number, StdDev, Obs, Definitive(1)/Provisional(0)
col_names = ['Year', 'MeanSunspotNumber', 'StdDev', 'Observations', 'Definitive']
sunspot_df = pd.read_csv(file_path, sep=';', header=None, names=col_names)
print("Data loaded successfully.")

# Convert Year column if it's not read as numeric (sometimes includes decimals like YYYY.5)
# We'll floor it to integer year for filtering and plotting
sunspot_df['YearInt'] = np.floor(sunspot_df['Year']).astype(int)

# --- Filter Data for 1960-2020 ---
print("Filtering data between 1960 and 2020...")
filtered_df = sunspot_df[(sunspot_df['YearInt'] >= 1960) & (sunspot_df['YearInt'] <= 2020)].copy()
print(f"Number of entries between 1960 and 2020: {filtered_df.shape[0]}")

if filtered_df.empty:
    print("ERROR: No data found in the range 1960-2020.")
else:
    print(f"Found {len(filtered_df)} yearly records in the specified range.")

    # --- Analyze Solar Cycle ---
    years = filtered_df['YearInt'].values
    ssn = filtered_df['MeanSunspotNumber'].values

    # Find peaks (maxima) - adjust prominence/distance as needed
    # Prominence: Minimum height difference to be considered a peak
    # Distance: Minimum horizontal distance between peaks
    maxima_indices, _ = find_peaks(ssn, prominence=20, distance=5)
    maxima_years = years[maxima_indices]
    maxima_ssn = ssn[maxima_indices]

    # Find troughs (minima) by finding peaks in the inverted signal
    minima_indices, _ = find_peaks(-ssn, prominence=20, distance=5)
    minima_years = years[minima_indices]
    minima_ssn = ssn[minima_indices]

    # Calculate average period between minima
    if len(minima_years) > 1:
        avg_period = np.mean(np.diff(minima_years))
        print(f"\nApproximate Average Solar Cycle Period (Min-to-Min): {avg_period:.2f} years")
    else:
        avg_period = "N/A (less than 2 minima found)"
        print("\nCould not calculate average period (less than 2 minima found).")

    print("\nApproximate Years of Activity Maxima (Peaks) in 1960-2020:")
    for year, val in zip(maxima_years, maxima_ssn):
        print(f"  - {year} (Mean SSN: {val:.1f})")

    print("\nApproximate Years of Activity Minima (Troughs) in 1960-2020:")
    for year, val in zip(minima_years, minima_ssn):
        print(f"  - {year} (Mean SSN: {val:.1f})")




