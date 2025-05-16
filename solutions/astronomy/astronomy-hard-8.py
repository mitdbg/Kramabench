#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import cdflib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# ---------------------------
# 1. Load OMNI Data (Kp and Pdyn)
# ---------------------------

def load_omni_file(filepath, column_name):
    data = []
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 4:  # only 4 columns
                year, doy, hour, value = parts[:4]
                dt = pd.to_datetime(f"{year}-{doy} {hour}", format="%Y-%j %H")
                data.append((dt, float(value)))
    df = pd.DataFrame(data, columns=["datetime", column_name])
    df.set_index("datetime", inplace=True)
    return df

# Load Kp Index (divide by 10)
kp_df = load_omni_file("./data/astronomy/input/omni2/omni2_Kp_Index.lst", "Kp")
kp_df["Kp"] /= 10.0
kp_df = kp_df.resample('h').mean()
print(f"kp_df rows: {kp_df.shape[0]}")

# Load Solar Wind Dynamic Pressure
p_dyn_df = load_omni_file("./data/astronomy/input/omni2/omni2_Flow_Pressure.lst", "Pdyn")
p_dyn_df = p_dyn_df.resample('h').mean()
print(f"Pdyn rows: {p_dyn_df.shape[0]}")

# ---------------------------
# 2. Load Swarm Alpha ACCACAL Data
# ---------------------------

cdf = cdflib.CDF("./data/astronomy/input/swarm/SW_OPER_ACCACAL_2__20240511T000000_20240511T235959_0304.cdf")

# Extract time and acceleration components
timestamp = cdf.varget("time")
acc_x = cdf.varget("a_cal")[:, 0]

# Convert CDF time to pandas datetime
time = pd.to_datetime(cdflib.cdfepoch.to_datetime(timestamp))

# Create DataFrame for acceleration
acc_df = pd.DataFrame({"datetime": time, "acc_x": acc_x}).set_index("datetime")

# Resample to 1-hour average to match OMNI data
acc_hourly = acc_df.resample("h").mean()
print(f"acc_hourly rows: {acc_hourly.shape[0]}")

# ---------------------------
# 3. Prepare the dataset
# ---------------------------

# Merge all datasets
full_df = acc_hourly.join([kp_df, p_dyn_df], how="inner").dropna()

# Shift target by -3 hours (forecast 3 hours ahead)
full_df["acc_x_target"] = full_df["acc_x"].shift(-3)
full_df = full_df.dropna()
print(f"Full df rows: {full_df.shape[0]}")


# Features and targets
if len(full_df) < 4:
    raise ValueError("Not enough data after merging and shifting for training and testing.")

X_kp = full_df[["Kp"]].values
X_pdyn = full_df[["Pdyn"]].values
y = full_df["acc_x_target"].values

# Train/test split (time ordered)
split_index = int(0.7 * len(full_df))

X_kp_train, X_kp_test = X_kp[:split_index], X_kp[split_index:]
X_pdyn_train, X_pdyn_test = X_pdyn[:split_index], X_pdyn[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

if len(X_kp_train) == 0 or len(X_kp_test) == 0 or len(X_pdyn_train) == 0 or len(X_pdyn_test) == 0:
    raise ValueError("Training or testing set is empty. Check the input data size.")

# ---------------------------
# 4. Train models
# ---------------------------

# Model 1: Kp only
model_kp = LinearRegression().fit(X_kp_train, y_train)
y_pred_kp = model_kp.predict(X_kp_test)

print(f"Kp model intercept: {model_kp.intercept_}")

# Model 2: Pdyn only
model_pdyn = LinearRegression().fit(X_pdyn_train, y_train)
y_pred_pdyn = model_pdyn.predict(X_pdyn_test)

print(f"pydn model intercept: {model_pdyn.intercept_}")

# ---------------------------
# 5. Evaluate
# ---------------------------

rmse_kp = np.sqrt(mean_squared_error(y_test, y_pred_kp))
rmse_pdyn = np.sqrt(mean_squared_error(y_test, y_pred_pdyn))

print(f"\nModel Performance (RMSE on Test Set):")
print(f"- Kp input: {rmse_kp:.4e}")
print(f"- Pdyn input: {rmse_pdyn:.4e}")




