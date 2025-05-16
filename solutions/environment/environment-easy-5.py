#!/usr/bin/env python
# coding: utf-8


import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"


year = 2020
regions = ["boston", 'chatham', 'amherst', 'ashburnham']
max_region = None
max_rainfall = -1
for region in regions:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{region}.csv")
    print(csv_path)
    df = pd.read_csv(csv_path)
    df = df[["Year", "Jun", "Jul", "Aug"]]
    # get year data
    df = df[df["Year"] == str(year)]
    # cast the month columns to float
    df["Jun"] = df["Jun"].astype(float)
    df["Jul"] = df["Jul"].astype(float)
    df["Aug"] = df["Aug"].astype(float)
    # get the sum of the three months
    df = df[["Jun", "Jul", "Aug"]].sum(axis=1)
    # get the value
    rainfall = df.values[0]
    if rainfall > max_rainfall:
        max_rainfall = rainfall
        max_region = region
print(f"The region with the most rainfall in {year} is {max_region} with {max_rainfall} inches.")



