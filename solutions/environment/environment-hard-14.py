#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"


start_year = 2007
end_year = 2010
marine_rates = []
fresh_rates = []
for year in range(start_year, end_year):
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)

    marine_df = df[df['Beach Type Description'] == 'Marine']
    fresh_df = df[df['Beach Type Description'] == 'Fresh']
    marine_ex = marine_df[marine_df['Violation'].str.lower() == 'yes']
    fresh_ex = fresh_df[fresh_df['Violation'].str.lower() == 'yes']
    marine_rate = len(marine_ex) / len(marine_df)
    fresh_rate = len(fresh_ex) / len(fresh_df)
    marine_rates.append(marine_rate)
    fresh_rates.append(fresh_rate)

marine_rates = np.array(marine_rates)
fresh_rates = np.array(fresh_rates)
print(f"Marine rates: {marine_rates}")
print(f"Fresh rates: {fresh_rates}")


months = ["Jun", "Jul", "Aug"]
marine_cities = ['boston', 'chatham']
fresh_cities = ["boston", 'chatham', 'amherst', 'ashburnham']

marine_rains = []
fresh_rains = []
for city in marine_cities:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{city}.csv")
    df = pd.read_csv(csv_path)
    df = df[["Year"]+months]
    # filter if Year in [2007, 2008, 2009]
    df = df[df['Year'].isin(["2007", "2008", "2009"])]
    # cast Jun, Jul, Aug to float
    for month in months:
        df[month] = df[month].astype(float)
    # sum per row
    df["Total"] = df[months].sum(axis=1)
    rainfall = list(df["Total"].values)
    marine_rains.append(rainfall)

marine_rains = np.array(marine_rains)
marine_rains = np.mean(marine_rains, axis=0)

print("Marine Rainfall:", marine_rains)

for city in fresh_cities:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{city}.csv")
    df = pd.read_csv(csv_path)
    df = df[["Year"]+months]
    # filter if Year in [2007, 2008, 2009]
    df = df[df['Year'].isin(["2007", "2008", "2009"])]
    # cast Jun, Jul, Aug to float
    for month in months:
        df[month] = df[month].astype(float)
    # sum per row
    df["Total"] = df[months].sum(axis=1)
    rainfall = list(df["Total"].values)
    fresh_rains.append(rainfall)
fresh_rains = np.array(fresh_rains)
fresh_rains = np.mean(fresh_rains, axis=0)
print("Fresh Rainfall:", fresh_rains)


# calculate correlation
marine_rain_corr = np.corrcoef(marine_rates, marine_rains)[0][1]
fresh_rain_corr = np.corrcoef(fresh_rates, fresh_rains)[0][1]
print("Marine Rainfall Correlation:", marine_rain_corr)
print("Fresh Rainfall Correlation:", fresh_rain_corr)



