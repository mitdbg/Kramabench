#!/usr/bin/env python
# coding: utf-8


# Question 1
import pandas as pd
import re
from pathlib import Path
from sklearn.metrics import mean_absolute_error

def extract_forecasted_ap(file_content):
    """Extract forecasted Ap from a forecast file."""
    match = re.search(r'Predicted Ap (\d{2}) Mar-(\d{2}) Mar\s+(\d+)-(\d+)-(\d+)', file_content)
    if match:
        return list(map(int, match.groups()[2:]))
    return []

def extract_observed_ap(file_content):
    """Extract observed Ap from a file."""
    match = re.search(r'Observed Ap (\d{2}) Mar\s+(\d+)', file_content)
    if match:
        return int(match.group(2))
    return None

def read_file(file_path):
    """Read a file as text."""
    with open(file_path, 'r') as f:
        return f.read()

# ---- Set paths ----
base_path = Path('../../data/astronomy/input/geomag_forecast') 
forecast_file = base_path / '0309geomag_forecast.txt'
# The observed value of the prior day is reported in the next day, 
# so we extract from Mar 11 to 13.
obs_files = [base_path / f'031{i}geomag_forecast.txt' for i in range(1, 4)]

# ---- Extract data ----
forecast_content = read_file(forecast_file)
forecasted_ap = extract_forecasted_ap(forecast_content)

observed_ap = []
for f in obs_files:
    content = read_file(f)
    ap = extract_observed_ap(content)
    observed_ap.append(ap)

# ---- Calculate MAE ----
forecast_series = pd.Series(forecasted_ap, name="Forecasted")
observed_series = pd.Series(observed_ap, name="Observed")

mae = mean_absolute_error(observed_series, forecast_series)

print("Forecasted Ap:", forecast_series.tolist())
print("Observed Ap:", observed_series.tolist())
print(f"Mean Absolute Error (MAE) from 03/09 forecast: {mae:.2f}")




