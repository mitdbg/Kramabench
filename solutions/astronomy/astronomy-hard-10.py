#!/usr/bin/env python
# coding: utf-8


# 1. Setup and Imports
import pandas as pd
import numpy as np
import glob
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# 2. Helper: Parse SP3 file for Swarm-A (PRN L47)
def parse_sp3(sp3_path):
    """
    Reads a Swarm-A SP3 file and returns a DataFrame with datetime and altitude.
    """
    times, xs, ys, zs = [], [], [], []
    current_time = None
    with open(sp3_path, 'r') as f:
        for line in f:
            if line.startswith('*'):
                ts_str = line[2:].strip()
                ts_parts = ts_str.split()
                date_str = ' '.join(ts_parts[:6])
                current_time = pd.to_datetime(date_str, format="%Y %m %d %H %M %S.%f")
            elif line.startswith('PL47'):
                parts = line.strip().split()
                if len(parts) >= 4:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    times.append(current_time)
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
    df = pd.DataFrame({
        'datetime': times,
        'X_km': xs,
        'Y_km': ys,
        'Z_km': zs
    }).set_index('datetime')
    df['alt_km'] = np.sqrt(df.X_km**2 + df.Y_km**2 + df.Z_km**2) - 6371.0
    return df[['alt_km']]

# 3. Build hourly change of altitude series
sp3_files = sorted(glob.glob(
    './data/astronomy/input/swarm/POD/SW_OPER_SP3ACOM_2__201810??T??????_201810??T??????_0201/*.sp3'
))
alt_dfs = [parse_sp3(fn) for fn in sp3_files]
alt_all = pd.concat(alt_dfs).sort_index()

# ensure datetime index
if not isinstance(alt_all.index, pd.DatetimeIndex):
    alt_all.index = pd.to_datetime(alt_all.index)

# Resample to hourly and compute delta altitude
alt_hourly = alt_all.resample('1h').mean().dropna()
alt_hourly['delta_alt'] = alt_hourly['alt_km'].diff()
alt_hourly = alt_hourly.dropna()
print(f"Swarm-A change of altitude records: {alt_hourly.shape}. Average change of altitude: {np.mean(alt_hourly['delta_alt'])}")

# 4. Load OMNI2 data
omni = pd.read_csv(
    './data/astronomy/input/STORM-AI/warmup/v2/OMNI2/omni2-wu590-20181001_to_20181130.csv',
    parse_dates=['Timestamp'],
    index_col='Timestamp'
)
omni10 = omni.loc['2018-10-01':'2018-10-10']
omni10 = omni10.resample('1h').mean().dropna()
print(f"OMNI2 records: {omni10.shape}")

# 5. Load Sat_Density
sd_files = sorted(glob.glob(
    './data/astronomy/input/STORM-AI/warmup/v2/Sat_Density/swarma-wu???-201810??_to_201810??.csv'
))
sd_list = []
for fn in sd_files:
    df = pd.read_csv(fn, parse_dates=['Timestamp'], index_col='Timestamp')
    df = df.rename(columns={'Orbit Mean Density (kg/m^3)': 'Orbit_Mean_Density'})
    sd_list.append(df.loc['2018-10-01':'2018-10-10'])
satdens = pd.concat(sd_list)
satdens = satdens.resample('1h').mean().dropna()
print(f"Sat_Density records: {satdens.shape}")

# 6. Merge change altitude, OMNI2, Sat_Density
df = (
    alt_hourly[['delta_alt']]
    .join(omni10, how='inner')
    .join(satdens, how='inner')
    .dropna()
)
print(f"Final merged dataset shape: {df.shape}")

if df.empty:
    raise RuntimeError("No overlapping data found.")

# 7. Compute Pearson correlations
corrs = {}
for col in df.columns:
    if col == 'delta_alt':
        continue
    if df[col].nunique() <= 1:
        continue  # Skip constant columns
    r, _ = pearsonr(df['delta_alt'], df[col])
    corrs[col] = r

# Find the strongest absolute correlation
best_metric = max(corrs, key=lambda k: abs(corrs[k]))
best_r = corrs[best_metric]

print("Most correlated metric:")
print(f"  {best_metric} (Pearson r = {best_r:.3f})")


