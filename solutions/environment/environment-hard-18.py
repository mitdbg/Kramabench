#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"


#    "query": "Is it true (answer with True or False) that the exceedance rate of fresh water beaches follow the same trend as the rainfall, from 2020 to 2023 (inclusive)? (e.g., they both increase and decrease together) Impute missing values with median of the month in non-missing years",


years = [2020, 2021, 2022, 2023]
months = ['Jun','Jul','Aug']
fresh_cities = ["boston", 'chatham', 'amherst', 'ashburnham']

fresh_rains = []
# calcuate rainfall first
for city in fresh_cities:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{city}.csv")
    df = pd.read_csv(csv_path)
    df = df[:27]
    df = df[["Year"]+months]
    # per column, impute "M" with median
    for month in months:
        df[month] = df[month].replace("M", np.nan)
        df[month] = df[month].astype(float)
        median = df[month].median()
        df[month] = df[month].fillna(median)
    df = df[df['Year'].isin(["2020", "2021", "2022", "2023"])]
    print(f"City: {city}")
    print(df)
    # cast Jun, Jul, Aug to float
    for month in months:
        df[month] = df[month].astype(float)
    # sum per row
    df["Total"] = df[months].sum(axis=1)
    rainfall = list(df["Total"].values)
    fresh_rains.append(rainfall)
fresh_rains = np.array(fresh_rains)
fresh_rains = np.sum(fresh_rains, axis=0)
print("Fresh Rainfall:", fresh_rains)



fresh_rates = []
for year in years:
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)

    fresh_df = df[df['Beach Type Description'] == 'Fresh']
    fresh_ex = fresh_df[fresh_df['Violation'].str.lower() == 'yes']
    fresh_rate = len(fresh_ex) / len(fresh_df)
    fresh_rates.append(fresh_rate)

fresh_rates = np.array(fresh_rates) * 100

def compute_trend(rates):
    trend = []
    for i in range(len(rates)-1):
        if rates[i] > rates[i+1]:
            trend.append(-1)
        elif rates[i] < rates[i+1]:
            trend.append(1)
        else:
            trend.append(0)
    return trend

fresh_trend = compute_trend(fresh_rates)
rain_trend = compute_trend(fresh_rains)

print("Exceedance Rates trend", fresh_trend)
print("Rainfall trend", rain_trend)
print("Do they follow the same trend?", bool(np.all(fresh_trend==rain_trend)))


