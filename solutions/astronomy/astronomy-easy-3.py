#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from glob import glob
import pathlib
import os

# ---- 1. Load altitude for each file ID -----------------------------------
init_df = (
    pd.read_csv("./data/astronomy/input/STORM-AI/warmup/v2/wu001_to_wu715-initial_states.csv", parse_dates=["Timestamp"])
      .loc[:, ["File ID", "Altitude (km)"]]
      .rename(columns={"File ID": "file_id", "Altitude (km)": "alt_km"})
)

# ---- 2. Collect Swarm-A density slices for 2015 ---------------------------
dens_frames = []
for f in glob("./data/astronomy/input/STORM-AI/warmup/v2/Sat_Density/swarma-*2015*.csv"):
    df = pd.read_csv(f, parse_dates=["Timestamp"])
    df = df[df.Timestamp.dt.year == 2015]
    if df.empty:
        continue

    # Clean invalid values: drop empty or 9.99e+32 
    # since density is never O(1e30), it's safe to discard all of them.
    df = df[pd.to_numeric(df["Orbit Mean Density (kg/m^3)"], errors='coerce').notna()]
    df["Orbit Mean Density (kg/m^3)"] = df["Orbit Mean Density (kg/m^3)"].astype(float)
    df = df[df["Orbit Mean Density (kg/m^3)"] < 1e30]  # discard large invalid values

    # Keep only timestamps at exactly 00:00
    df = df[df.Timestamp.dt.time == pd.to_datetime("00:00:00").time()]
    
    file_id = pathlib.Path(f).stem.split("-")[1]
    df["file_id"] = file_id
    dens_frames.append(df[["Timestamp", "file_id", "Orbit Mean Density (kg/m^3)"]])

if dens_frames:
    dens_df = pd.concat(dens_frames, ignore_index=True)
    print(f"Dens DF length: {dens_df.shape[0]}")
else:
    raise ValueError("No valid Swarm-A density data found for 2015.")

# ---- 3. Join with altitude and compute mean for 450–500 km range ---------
merged = dens_df.merge(init_df, on="file_id", how="left")
print(f"Merged DF length: {merged.shape[0]}")
slice_ = merged[merged.alt_km.between(450, 500)]
mean_rho = slice_["Orbit Mean Density (kg/m^3)"].mean()

print(f"Swarm‑Alpha mean density (400–450 km, 00:00 UTC, 2015): {mean_rho:.3e} kg/m^3")




