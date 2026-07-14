#!/usr/bin/env python
# coding: utf-8

# Alternative solution for astronomy-easy-2 that covers the FULL calendar days
# named in the query. The 3-day density files end exactly at midnight of their
# final day, so swarma-wu016 / swarma-wu545 contain only the first instant of
# March 17 2014 / July 21 2018. The remainder of those days lives in the
# subsequent files (swarma-wu017 / swarma-wu546); the true July peak occurs on
# 2018-07-21 13:10:00 and is only visible there.

import pandas as pd
import os

# --- Configuration ---
BASE_DATA_DIR = '../../data/astronomy/input/STORM-AI/warmup/v2/'
DENSITY_DIR = os.path.join(BASE_DATA_DIR, 'Sat_Density/')

# Files covering each period, including the day that spills into the next file
PERIOD_1_FILES = [  # March 14th-17th 2014
    'swarma-wu016-20140314_to_20140317.csv',
    'swarma-wu017-20140317_to_20140320.csv',
]
PERIOD_2_FILES = [  # July 18th-21st 2018
    'swarma-wu545-20180718_to_20180721.csv',
    'swarma-wu546-20180721_to_20180724.csv',
]
PERIOD_1_WINDOW = ('2014-03-14', '2014-03-18')  # [start, end)
PERIOD_2_WINDOW = ('2018-07-18', '2018-07-22')

DENSITY_COL = 'Orbit Mean Density (kg/m^3)'
TIME_COL = 'Timestamp'


# --- Function to Load and Find Peak ---
def find_peak_density(file_names, window, density_col_name, time_col_name):
    """Loads the files, restricts to the window, and returns the peak density."""
    frames = []
    for name in file_names:
        path = os.path.join(DENSITY_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        print(f"Loading data from: {path}")
        frames.append(pd.read_csv(path, parse_dates=[time_col_name]))
    df = pd.concat(frames, ignore_index=True).sort_values(by=time_col_name)

    if density_col_name not in df.columns:
        raise ValueError(f"Density column '{density_col_name}' not found.")

    # Clean invalid measurements (n/a values or 9.99E32 sentinels)
    df[density_col_name] = pd.to_numeric(df[density_col_name], errors='coerce')
    df = df[df[density_col_name].notna() & (df[density_col_name] < 1e30)]

    start, end = window
    df = df[(df[time_col_name] >= start) & (df[time_col_name] < end)]
    if df.empty:
        raise ValueError(f"No data in window {window}")

    peak_density = df[density_col_name].max()
    peak_time = df.loc[df[density_col_name].idxmax(), time_col_name]
    print(f"  Peak density found: {peak_density:.3e} at {peak_time}")
    return peak_density


# --- Load Data and Analyze ---
try:
    peak_1 = find_peak_density(PERIOD_1_FILES, PERIOD_1_WINDOW, DENSITY_COL, TIME_COL)
    peak_2 = find_peak_density(PERIOD_2_FILES, PERIOD_2_WINDOW, DENSITY_COL, TIME_COL)

    # --- Compare Peaks ---
    print(f"\n--- Peak Density Comparison ---")
    print(f"Peak Density in Period 1 (March 14th-17th 2014): {peak_1:.3e}")
    print(f"Peak Density in Period 2 (July 18th-21st 2018): {peak_2:.3e}")

    if peak_1 > 0:  # Avoid division by zero if peak1 is zero or negative
        ratio = peak_1 / peak_2
        print(f"Ratio (Peak 1 / Peak 2): {ratio:.3f}")
    else:
        print("Cannot calculate ratio as Peak 1 is zero or negative.")

except FileNotFoundError as fnf_error:
    print(f"ERROR: {fnf_error} - Please ensure file names and paths are correct.")
except ValueError as ve:
    print(f"ERROR: Data processing error - {ve}")
except KeyError as ke:
    print(f"ERROR: Column name not found - {ke}. Please verify column names.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
