#!/usr/bin/env python
# coding: utf-8


import re
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# --------------- data files -------------------------------------------------
BASE_OMNI = Path("./data/astronomy/input/STORM-AI/warmup/v2/OMNI2").expanduser()
BASE_GOES = Path("./data/astronomy/input/STORM-AI/warmup/v2/GOES").expanduser()
BASE_DENS = Path("./data/astronomy/input/STORM-AI/warmup/v2/Sat_Density").expanduser()

TRAIN_ID  = "wu334"
TEST_ID   = "wu335"
DATE_RE   = re.compile(r"(\d{8})_to_(\d{8})")

# --------------- helper -----------------------------------------------------
def span_overlap(s1, e1, s2, e2):
    return not (e1 < s2 or e2 < s1)

def files_covering(folder, prefix, start, end):
    sel = []
    for f in folder.glob(f"*{prefix}*"):
        m = DATE_RE.search(f.name);  0
        if not m: continue
        s, e = map(pd.Timestamp, m.groups())
        if span_overlap(s, e, start, end): sel.append(f)
    if not sel:
        raise FileNotFoundError(f"{prefix}: no files for {start:%Y%m%d}-{end:%Y%m%d}")
    return sorted(sel)

# --------------- columns ----------------------------------------------------
OMNI_COLS = ["f10.7_index", "Kp_index", "Dst_index_nT"]
GOES_COLS = ["xrsb_flux_observed", "xrsa_flux_observed", ]
FEATS     = OMNI_COLS + GOES_COLS               

# --------------- loader -----------------------------------------------------
def load_df(fid, start, end):
    omni = pd.concat(pd.read_csv(p, parse_dates=["Timestamp"])
                     for p in files_covering(BASE_OMNI, f"omni2-{fid}", start, end))\
            [["Timestamp"] + OMNI_COLS]
    omni['Kp_index'] /= 10

    goes = pd.concat(pd.read_csv(p, parse_dates=["Timestamp"])
                     for p in files_covering(BASE_GOES, f"goes-{fid}", start, end))\
            [["Timestamp"] + GOES_COLS]

    dens = pd.concat(pd.read_csv(p, parse_dates=["Timestamp"])
                     for p in files_covering(BASE_DENS, f"swarma-{fid}", start, end))\
            [["Timestamp", "Orbit Mean Density (kg/m^3)"]]\
            .rename(columns={"Orbit Mean Density (kg/m^3)": "rho"})

    return (omni.merge(goes, on="Timestamp", how="inner")
                .set_index("Timestamp")
                .sort_index()
                .resample("1h").mean(), 
            dens.set_index("Timestamp")
                .sort_index().resample("1h").mean()
           )

# --------------- windows ----------------------------------------------------
tr_start, tr_end   = pd.Timestamp("20161022"), pd.Timestamp("20161023")
tr_rho_end         = tr_end + timedelta(days=1)

te_start, te_end   = pd.Timestamp("20161025"), pd.Timestamp("20161026")
te_rho_end         = te_end + timedelta(days=1)

train_df, train_dens = load_df(TRAIN_ID, tr_start, tr_rho_end)
test_df, test_dens  = load_df(TEST_ID,  te_start, te_rho_end)

print(f"Length of each DF: train_df {train_df.shape[0]}, test_df {test_df.shape[0]}, train_dens {train_dens.shape[0]}, test_dens {test_dens.shape[0]}")

# --------------- sample --------------------------------------------
HIST = 16   # h of context
H = 4       # forecast horizon

def samples(df):
    df = df.copy()
    rows = []
    win = df.loc[df.index[-HIST]:df.index[-1], FEATS]

    # VAR(1) coefficients A (k×k)
    Y, X = win.iloc[1:].values, win.iloc[:-1].values
    A    = np.linalg.lstsq(X, Y, rcond=None)[0].T
    y1   = (A @ win.iloc[-1].values.reshape(-1,1)).ravel()  # +1 h forecast
    for _ in range(H): 
        rows.append(y1)
        y1 = (A @ y1).ravel()

    cols = [f"{c}_f1h" for c in FEATS]
    return pd.DataFrame(rows, columns=cols)

train_s   = samples(train_df)
test_s    = samples(test_df)

# --------------- linear regressor ---------------------------------------
poly  = PolynomialFeatures(degree=1, include_bias=False)
X_tr  = poly.fit_transform(train_s[[f"{c}_f1h" for c in FEATS]])
y_tr  = train_dens["rho"][1:1+H].values
reg   = LinearRegression().fit(X_tr, y_tr)
print(f"Max projected F10.7 in wu334 in the next hour: {max(X_tr.T[0])}")
print(f"rmse for the training data: {mean_squared_error(y_tr, reg.predict(X_tr)) ** (1/2)}")

X_te  = poly.transform(test_s[[f"{c}_f1h" for c in FEATS]])
y_te  = test_dens["rho"][1:1+H].values
print(f"Max projected F10.7 in wu335 in the next hour: {max(X_te.T[0])}")
rmse   = mean_squared_error(y_te, reg.predict(X_te)) ** (1/2)

print(f"rMSE for {H}-hour density prediction  –  train {TRAIN_ID}, test {TEST_ID}: {rmse: .3e}")




