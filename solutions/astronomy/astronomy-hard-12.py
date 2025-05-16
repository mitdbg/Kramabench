#!/usr/bin/env python
# coding: utf-8


# 1. Setup and Imports
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# Constants
R_EARTH = 6371.0  # Earth radius in km
G = 9.80665       # m/s^2, standard gravity

# 2. Load SP3 Data for Swarm-A

def parse_sp3(sp3_path):
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
    df['alt_km'] = np.sqrt(df.X_km**2 + df.Y_km**2 + df.Z_km**2) - R_EARTH
    df['lat_deg'] = np.degrees(np.arcsin(df.Z_km / (df.alt_km + R_EARTH)))
    df['lon_deg'] = np.degrees(np.arctan2(df.Y_km, df.X_km))
    return df[['lat_deg', 'lon_deg', 'alt_km']]

# 3. Load all SP3 files
sp3_files = sorted(glob.glob('./data/astronomy/input/swarm/POD/SW_OPER_SP3ACOM_2__201909??T??????_201909??T??????_0201/*.sp3'))
alt_dfs = [parse_sp3(fn) for fn in sp3_files]
traj_df = pd.concat(alt_dfs).sort_index()
traj_df = traj_df.loc['2019-09-02':'2019-09-29']
print(f"Swarm-A Trajectory Loaded: {traj_df.shape}")

# 4. Prepare mock TIE-GCM grid (normally output from a simulation)
# (Here, we mock it since TIE-GCM simulation is heavy)
grid_data = np.load('./data/astronomy/input/mock_tiegcm_grid_sept2019.npz')
lat_grid = grid_data['lat_grid']
lon_grid = grid_data['lon_grid']
alt_grid = grid_data['alt_grid']

print(f"Mean of alt grid: {np.mean(alt_grid)}")

# Mock geopotential field (J/kg) as function of alt (higher -> more potential energy)
geopotential_grid = np.zeros((len(lat_grid), len(lon_grid), len(alt_grid)))
for i, alt in enumerate(alt_grid):
    geopotential_grid[:, :, i] = G * (R_EARTH*1000 + alt*1000)  # in m^2/s^2

# 5. Interpolate geopotential to Swarm-A trajectory
interpolator = RegularGridInterpolator((lat_grid, lon_grid, alt_grid), geopotential_grid, bounds_error=False, fill_value=None)

# Make sure longitudes are 0-360
traj_df['lon_deg'] = traj_df['lon_deg'] % 360

points = traj_df[['lat_deg', 'lon_deg', 'alt_km']].values
geopotential_at_satellite = interpolator(points)

traj_df['geopotential_J_per_kg'] = geopotential_at_satellite

# 6. Compute final answer
mean_geopotential = traj_df['geopotential_J_per_kg'].mean()
print("\n Final Result:")
print(f"Mean Geopotential Energy: {mean_geopotential:.2f} J/kg")



