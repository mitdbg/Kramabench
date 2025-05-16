#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"

# "query": "For marine beaches, is the year with the highest average exceedance rate difference (with the previous year) different or the same as the highest total rainfall difference (with the previous year)? Only count the rainfall in June, July, August in Boston and Chatham; impute missing values with median of the month in non-missing years. Answer with True or False.",

beach_type = "Marine"
start_year = 2002
end_year = 2024
rates = []
for year in range(start_year, end_year):
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)
    beach_df = df[df['Beach Type Description'] == beach_type]
    ex_df = beach_df[beach_df['Violation'].str.lower() == 'yes']
    rate = len(ex_df) / len(beach_df)
    rates.append(rate)

rates = np.array(rates)

# Find the most difference between the years
rate_max_diff = np.max(np.abs(np.diff(rates)))
# Find the year with the most difference
rate_max_diff_year = np.argmax(np.abs(np.diff(rates))) + start_year + 1
print(rates)
print(rate_max_diff)
print(f"Year with the most difference: from {rate_max_diff_year} to {rate_max_diff_year + 1}")


months = ['Jun','Jul','Aug']
cities = ["boston", 'chatham']

rains = []
# calcuate rainfall first
for city in cities:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{city}.csv")
    df = pd.read_csv(csv_path)
    df = df[2:24]
    df = df[["Year"]+months]
    # filter if Year in [2007, 2008, 2009]
    # per column, impute "M" with median
    for month in months:
        df[month] = df[month].replace("M", np.nan)
        df[month] = df[month].astype(float)
        median = df[month].median()
        df[month] = df[month].fillna(median)
    print(f"City: {city}")
    print(df)
    # cast Jun, Jul, Aug to float
    for month in months:
        df[month] = df[month].astype(float)
    # sum per row
    df["Total"] = df[months].sum(axis=1)
    rainfall = list(df["Total"].values)
    rains.append(rainfall)
rains = np.array(rains)
rains = np.sum(rains, axis=0)
print("Rainfall:", rains)


# Find the most difference between the years
rain_max_diff = np.max(np.abs(np.diff(rains)))
# Find the year with the most difference
max_diff_year_rain = np.argmax(np.abs(np.diff(rains))) + start_year + 1
print(rains)
print(rain_max_diff)
print(f"Year with the most difference: from {max_diff_year_rain} to {max_diff_year_rain + 1}")

# Compare the two years
print(f"Year with the most difference: {max_diff_year_rain+1} and {rate_max_diff_year+1}. Is it the same? {max_diff_year_rain == rate_max_diff_year}")
