#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from skyfield.api import load, EarthSatellite
from pathlib import Path
from scipy.stats import linregress  # convenient way to get r

# ------------------------------------------------------------------
# 1.  OMNI-2 : hourly AP index for May 2024
# ------------------------------------------------------------------
omni = pd.read_fwf(
    Path("./data/astronomy/input/omni2_low_res/omni2_2024.dat").expanduser(),  # << path
    widths=[
        4,
        4,
        3,
        5,
        3,
        3,
        4,
        4,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        9,
        6,
        6,
        6,
        6,
        6,
        6,
        9,
        6,
        6,
        6,
        6,
        6,
        7,
        7,
        6,
        3,
        4,
        6,
        5,
        10,
        9,
        9,
        9,
        9,
        9,
        3,
        4,
        6,
        6,
        6,
        6,
        5,
    ],
    header=None,
)
omni.columns = [
    "year",
    "doy",
    "hour",
    "brn",
    "imf_id",
    "sw_id",
    "n_imf",
    "n_sw",
    "B_mag_avg",
    "B_vec_mag",
    "B_lat",
    "B_long",
    "Bx_GSE",
    "By_GSE",
    "Bz_GSE",
    "By_GSM",
    "Bz_GSM",
    "sigma_B_mag",
    "sigma_B_vec",
    "sigma_Bx",
    "sigma_By",
    "sigma_Bz",
    "proton_temp",
    "proton_density",
    "flow_speed",
    "flow_long",
    "flow_lat",
    "Na_Np",
    "flow_pressure",
    "sigma_T",
    "sigma_N",
    "sigma_V",
    "sigma_phi_V",
    "sigma_theta_V",
    "sigma_Na_Np",
    "electric_field",
    "plasma_beta",
    "alfven_mach",
    "Kp",
    "sunspot",
    "Dst",
    "AE",
    "pf_1MeV",
    "pf_2MeV",
    "pf_4MeV",
    "pf_10MeV",
    "pf_30MeV",
    "pf_60MeV",
    "flag",
    "ap",
    "f10.7",
    "PC_N",
    "AL",
    "AU",
    "mach_number",
]

print(f"Number of columns in OMNI2: {len(omni.columns)}")

omni["Kp"] /= 10
omni["t"] = omni.apply(
    lambda r: datetime(int(r.year), 1, 1, tzinfo=timezone.utc)
    + timedelta(days=r.doy - 1, hours=r.hour),
    axis=1,
)


omni = (
    omni.set_index("t").sort_index().loc["2024-04-01":"2024-06-30 23:59", ["ap"]]
)  # May 2024 only


# ------------------------------------------------------------------
# 2.  TLEs for SATCAT 43180
# ------------------------------------------------------------------
def read_tle_pairs(fname):
    lines = [l.strip() for l in open(fname) if l.strip()]
    assert len(lines) % 2 == 0, "TLE file has an odd #lines"
    return [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]


def semi_major_axis_km(sat):
    μ = 398_600.4418  # km^3/s^2
    n = sat.model.no_kozai  # rad/min (see SGP4 docs)
    n_rad_s = n / 60
    return (μ / n_rad_s**2) ** (1 / 3)


ts = load.timescale()
tle_pairs = read_tle_pairs(
    Path("./data/astronomy/input/TLE/43180.tle").expanduser()
)  # << path

semi_major_km = []
epoch = []

for l1, l2 in tle_pairs:
    s = EarthSatellite(l1, l2, ts=ts)
    semi_major_km.append(semi_major_axis_km(s))
    epoch.append(s.epoch.utc_datetime())

print(f"average semi axis: {np.mean(semi_major_km)}")

START = pd.Timestamp("2024-05-01", tz="UTC")
END = pd.Timestamp("2024-06-01", tz="UTC")

df_tle = (
    pd.DataFrame({"epoch": epoch, "semi_major_km": np.array(semi_major_km)})
    .sort_values("epoch")
    .loc[lambda df: (df["epoch"] >= START) & (df["epoch"] < END)]
)

# ------------------------------------------------------------------
# 3.  semi_majoritude *change* between successive TLEs
#     assign the change to the second epoch in every pair
# ------------------------------------------------------------------
df_tle["semi_major_change"] = df_tle["semi_major_km"].diff()
df_tle = df_tle.dropna(subset=["semi_major_change"])

print(f"average change in semi axis: {np.mean(df_tle['semi_major_change'])}")

# ------------------------------------------------------------------
# 4.  Round TLE epochs to the nearest hour to match OMNI sampling
#     (>= 30 min goes up, < 30 min goes down)
# ------------------------------------------------------------------
df_tle["time_hr"] = pd.to_datetime(df_tle["epoch"]).dt.round("h")
df_tle = df_tle.set_index("time_hr")[["semi_major_change"]]

# If multiple TLEs land in the same hour, average their delta h
df_tle = df_tle.groupby("time_hr").mean()

ap = omni["ap"]  # hourly AP, tz-aware, index is datetime
semi_major_change = df_tle["semi_major_change"]  # hourly delta h, same time basis
# -----------------------------------------------------------

import pandas as pd
from scipy.stats import linregress

best_lag = None
best_r2 = -1
r2_curve = {}  # optional: keep the whole curve

for lag in range(0, 48):  # 0 … 24 h inclusive
    # shift AP *forward* by <lag> h → an AP value at hour t influences delta h at t+lag
    ap_lag = ap.copy()
    ap_lag.index = ap_lag.index + pd.Timedelta(hours=lag)

    joined = semi_major_change.to_frame("semi_major_change").join(
        ap_lag.rename("ap"), how="inner"
    )
    if len(joined) < 2:  # need at least 2 points for r
        continue

    r = joined["semi_major_change"].corr(joined["ap"])
    r2 = r * r
    r2_curve[lag] = r2

    if r2 > best_r2:
        best_r2, best_lag = r2, lag

print(f"best lag = {best_lag} h   with  r^2 = {best_r2:.4f}")
