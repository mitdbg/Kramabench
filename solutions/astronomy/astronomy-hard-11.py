#!/usr/bin/env python
# coding: utf-8


import numpy as np
from astropy.time import Time

from pyatmos.msise.nrlmsise00_subfunc import gtd7,gtd7d
from pyatmos.utils.utils import wraplon,hms_conver
from pyatmos.class_atmos import ATMOS

def nrlmsise00(t,
               location,
               f107A, 
               f107,
               ap,
               aph,
               aphmode=True):
    """
    This function is extracted from the nrlmsise00 algorithm from
    pyatmos, that takes external F10.7A, F10.7, AP and AP_H data.
    """

    lat,lon,h = location

    # calculate the altitude above sea level from height
    alt = h
        
    t = Time(t)
    t_ymd = t.isot.split('T')[0]
    t_yday = t.yday.split(':')
    year,doy = int(t_yday[0]),int(t_yday[1])
    hour,sec = hms_conver(int(t_yday[2]),int(t_yday[3]),float(t_yday[4]))
    lst = hour + wraplon(lon)/15
    if alt <= 80:
        f107A,f107,ap,aph = 150,150,4,np.full(7,4)

    lon_wrap = wraplon(lon)
    inputp = {'doy':doy,'year':year,'sec':sec,'alt':alt,'g_lat':lat,'g_lon':lon_wrap,'lst':lst,\
              'f107A':f107A,'f107':f107,'ap':ap,'ap_a':aph}
    
    switches = np.ones(23)
    if aphmode: switches[8] = -1 # -1 indicates the use of 3h geomagnetic index
        
    if alt > 500:
        output = gtd7d(inputp,switches)
    else:
        output = gtd7(inputp,switches)

    inputp['g_lon'] = lon   
    params = {'Year':inputp['year'],'DOY':inputp['doy'],'SOD':inputp['sec'],'Lat':inputp['g_lat'],'Lon':inputp['g_lon'],'Alt':inputp['alt'],'LST':inputp['lst'],\
              'f107A':inputp['f107A'],'f107D':inputp['f107'],'ApD':inputp['ap'],'Ap3H':inputp['ap_a']}
    rho = output['d']['RHO']          
    T = (output['t']['TINF'],output['t']['TG'])
    nd = {'He':output['d']['He'],'O':output['d']['O'],'N2':output['d']['N2'],'O2':output['d']['O2'],'Ar':output['d']['AR'],'H':output['d']['H'],'N':output['d']['N'],'ANM O':output['d']['ANM O']}

    info = {'rho':rho,'T':output['t']['TG'],'nd':nd}

    return ATMOS(info)


# In[2]:


import pandas as pd
from datetime import timedelta, timezone

import numpy as np
import pandas as pd
from datetime import timedelta, timezone, datetime

# ------------------------------------------------------------------
# helper : mean Ap for the 3-hour window that starts at `t_bin_start`
# ------------------------------------------------------------------
def _mean_ap3h(omni: pd.DataFrame, t_bin_start: datetime) -> float:
    """Return the average Ap over [t, t+3 h)."""
    win = omni.loc[t_bin_start : t_bin_start + timedelta(hours=3) - timedelta(seconds=1), 'ap']
    return float(win.mean())

# ------------------------------------------------------------------
# main entry --------------------------------------------------------
def build_msis_inputs(omni: pd.DataFrame, when_utc: datetime) -> dict:
    """
    Build NRLMSISE-00 inputs from an hourly OMNI-2 dataframe.

    Parameters
    ----------
    omni : DataFrame with columns 'f10.7' and 'ap'; index UTC & monotonic.
    when_utc : datetime (tz-aware)  – model evaluation time.

    Returns dict with keys: f107A, f107, ap, aph (np.ndarray len 7).
    These are data needed for the nrlmsise-00
    according to https://www.mathworks.com/help/aeroblks/nrlmsise00atmospheremodel.html
    """
    if when_utc.tzinfo is None:
        raise ValueError("`when_utc` must be timezone-aware (UTC)")

    # ---------- daily values --------------------------------------
    day          = when_utc.date()
    day_rows     = omni.index.date == day
    if not day_rows.any():
        raise ValueError("No OMNI data for that day")

    # “daily Ap” = mean of AP measurement
    ap_daily = float(omni.loc[day_rows, 'ap'].mean())
    # daily F10.7 is in the 00:00 UT row
    f107       = float(omni.loc[day_rows, 'f10.7'].iloc[0])

    # 81-day running average of F10.7 **up to but not including today**
    start81    = day - timedelta(days=81)
    mask81     = (omni.index.date >= start81) & (omni.index.date < day)
    f107A_ser  = (omni.loc[mask81, 'f10.7']
                       .groupby(omni.loc[mask81].index.date).first())
    f107A      = float(f107A_ser.mean()) if len(f107A_ser) == 81 else None

    # ---------- 3-hour Ap vector (aph[1] … aph[6]) ----------------
    # find the start of the 3-hour bin that contains `when_utc`
    t0 = when_utc.replace(minute=0, second=0, microsecond=0)
    bin_start_now = t0 - timedelta(hours=t0.hour % 3)

    def ap3(shift_h):
        return _mean_ap3h(omni, bin_start_now - timedelta(hours=shift_h))

    aph = np.empty(7, dtype=float)
    aph[0] = ap_daily
    aph[1] = ap3(0)          # centred on model time
    aph[2] = ap3(3)
    aph[3] = ap3(6)
    aph[4] = ap3(9)

    # mean of 8 bins whose centres lie 26 - 57 h before model time
    bins = [ap3(h) for h in range(12, 34, 3)]
    aph[5] = float(np.mean(bins))

    # mean of 8 bins whose centres lie 26 - 57 h before model time
    bins = [ap3(h) for h in range(36, 58, 3)]
    aph[6] = float(np.mean(bins))

    return {
        "f107A": f107A,
        "f107":  f107,
        "ap":    ap_daily,
        "aph":   aph,
    }


# In[3]:


from pathlib import Path
import pandas as pd
import numpy as np
import re

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def load_swarmb_density_year(folder: str | Path, year: int) -> pd.DataFrame:
    """
    Load every Swarm-B neutral-density POD text file for the given *year*
    into a single tidy DataFrame.

    Parameters
    ----------
    folder : str | Path
        Directory that contains files named like
        `SB_DNS_POD_yyyy_mm_v02.txt` (or .asc, .dat, …―wild-cards ok).
    year : int
        Four-digit year (e.g. 2024).

    Returns
    -------
    pandas.DataFrame
        Columns exactly match those in the files:
        ['alt_m', 'lon_deg', 'lat_deg', 'lst_h',
         'arglat_deg', 'rho_kg_m3', 'time_system'],
        indexed by timezone-aware pandas.DatetimeIndex (UTC),
        sorted in ascending order.
    """
    folder = Path(folder).expanduser()
    pattern = re.compile(rf"SB_DNS_POD_{year:04d}_(\d{{2}}).*\.txt$", re.I)

    # ---------------- Collect files ----------------
    files = sorted(p for p in folder.iterdir() if pattern.match(p.name))
    if not files:
        raise FileNotFoundError(f"No Swarm-B POD files for {year} in {folder}")

    frames = []
    for fp in files:
        # Skip comment header lines beginning with '#'
        with fp.open("r", encoding="utf-8") as fh:
            skip = 0
            for line in fh:
                if not line.startswith("#"):
                    break
                skip += 1

        # Fixed-width columns separated by *one* space ⇒ use delim_whitespace
        df = pd.read_csv(
            fp,
            sep=r'\s+',
            skiprows=skip,
            header=None,
            names=[
                "date", "time", "time_system",
                "alt_m", "lon_deg", "lat_deg",
                "lst_h", "arglat_deg", "rho_kg_m3"
            ],
            dtype={
                "time_system": "category",
                "alt_m": np.float64,
                "lon_deg": np.float64,
                "lat_deg": np.float64,
                "lst_h": np.float32,
                "arglat_deg": np.float64,
                "rho_kg_m3": np.float64,
            },
        )

        # Combine date+time, make timezone-aware (treat GPS as UTC)
        ts = pd.to_datetime(df["date"] + " " + df["time"], utc=True)
        df.index = ts
        frames.append(df.drop(columns=["date", "time"]))

    # ---------------- Concatenate & sort ----------------
    out = (
        pd.concat(frames, copy=False)
        .sort_index()
        .rename_axis("datetime_utc")
    )
    return out


# In[4]:


from pathlib import Path
from datetime import timezone
import numpy as np
import pandas as pd

omni = pd.read_fwf(
    Path("./data/astronomy/input/omni2_low_res/omni2_2024.dat").expanduser(),          # << path
    widths=[4, 4, 3, 5, 3, 3, 4, 4, 6, 6, 6, 6,
            6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
            9, 6, 6, 6, 6, 6, 6, 9, 6, 6, 
            6, 6, 6, 7, 7, 6,
            3, 4, 6, 5, 10, 9, 9, 9, 9, 9, 3,
            4, 6, 6, 6, 6, 5], header=None
)
omni = pd.concat([omni, pd.read_fwf(
    Path("./data/astronomy/input/omni2_low_res/omni2_2023.dat").expanduser(),          # << path
    widths=[4, 4, 3, 5, 3, 3, 4, 4, 6, 6, 6, 6,
            6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
            9, 6, 6, 6, 6, 6, 6, 9, 6, 6, 
            6, 6, 6, 7, 7, 6,
            3, 4, 6, 5, 10, 9, 9, 9, 9, 9, 3,
            4, 6, 6, 6, 6, 5], header=None
)])
omni.columns = [
    'year', 'doy', 'hour', 'brn', 'imf_id', 'sw_id', 'n_imf', 'n_sw', 
    'B_mag_avg', 'B_vec_mag', 'B_lat', 'B_long',
    'Bx_GSE', 'By_GSE', 'Bz_GSE', 'By_GSM', 'Bz_GSM',
    'sigma_B_mag', 'sigma_B_vec', 'sigma_Bx', 'sigma_By', 'sigma_Bz',
    'proton_temp', 'proton_density', 'flow_speed', 'flow_long', 'flow_lat',
    'Na_Np', 'flow_pressure', 'sigma_T', 'sigma_N', 'sigma_V',
    'sigma_phi_V', 'sigma_theta_V', 'sigma_Na_Np',
    'electric_field', 'plasma_beta', 'alfven_mach',
    'Kp', 'sunspot', 'Dst', 'AE', 'pf_1MeV', 'pf_2MeV', 'pf_4MeV', 'pf_10MeV', 'pf_30MeV', 'pf_60MeV', 'flag',
    'ap', 'f10.7', 'PC_N', 'AL', 'AU', 'mach_number'
]
omni['Kp'] /= 10

print(f"OMNI2 {omni.shape}")

omni['t'] = omni.apply(
    lambda r: datetime(int(r.year), 1, 1, tzinfo=timezone.utc)
              + timedelta(days=r.doy-1, hours=r.hour),
    axis=1
)

omni = (omni
        .set_index('t').sort_index())

# ---------------------------------------------------------------------
# 1.  INPUTS -----------------------------------------------------------
#    – omni  : hourly OMNI-2 dataframe (tz-aware, UTC, monotonic)
#    – build_msis_inputs : function we wrote earlier
#    – nrlmsise00        : user-supplied wrapper that returns .rho
#    – load_swarmb_density_year (given in the prompt)
# ---------------------------------------------------------------------

# --- a)  Swarm-B neutral density for 2024 -----------------------------
swarm_folder = "./data/astronomy/input/swarmb"           #  << your path
swarm = load_swarmb_density_year(swarm_folder, 2024)

# average everything to the *nearest* whole hour
swarm_hr = swarm[(swarm.index.minute == 0) &
                 (swarm.index.second == 0) &
                 (swarm.index.microsecond == 0)].copy()

print(f"swarm_hr shape {swarm_hr.shape}")


# --- b)  make sure OMNI covers 81 d back from 2024-01-01 --------------
first_needed = pd.Timestamp("2023-10-12", tz="UTC")   # 81 d before 2024-01-01
if omni.index.min() > first_needed:
    raise ValueError("OMNI file does not start early enough for f107A")

# ---------------------------------------------------------------------
# 2.  SCAN EVERY HOUR, RUN MODEL, COLLECT PREDICTIONS ------------------
# ---------------------------------------------------------------------
pred, obs = [], []

all_f107a = []

for ts, row in swarm_hr.iterrows():
    try:
        inp = build_msis_inputs(omni, ts)      # may raise if day missing
        if inp["f107A"] is None:               # skip until 81-day window exists
            continue
        all_f107a.append(inp["f107A"])
        
    except Exception:
        continue                               # skip hours missing OMNI data

    location = (
        row["lat_deg"],
        row["lon_deg"],
        row["alt_m"] / 1000.0                  # MSIS expects altitude [km]
    )

    rho_model = nrlmsise00(
        ts.to_pydatetime(), location,
        inp["f107A"], inp["f107"],
        inp["ap"],   inp["aph"],
        aphmode=True
    ).rho

    pred.append(rho_model)
    obs .append(row["rho_kg_m3"])

pred = np.asarray(pred)
obs  = np.asarray(obs)

print(f"mean of F10.7A {np.mean(all_f107a)}")

rmse = float(np.sqrt(np.mean((pred - obs) ** 2)))
print(f"NRLMSISE-00 RMSE vs Swarm-B for 2024  :  {rmse:.3e}  kg/m^3")


