#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input/"

#     "query": "What is the seasonal exceedance rate (in percentage, to 2 decimal places) of Chatham's Bucks Creek Beach in the summer (June, July, August) with the most rainfall in its area? Impute missing values with median of the month in non-missing years.",


city = 'chatham'
beach_name = 'Bucks Creek'

rainfall_df = pd.read_csv(os.path.join(data_path, f"monthly_precipitations_{city}.csv"))
months = ["Jun", "Jul", "Aug"]
rainfall_df = rainfall_df[["Year"]+months]
# cast Jun, Jul, Aug to float
rainfall_df = rainfall_df[rainfall_df['Year'].isin(["2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"])]
rainfall_df[months] = rainfall_df[months].astype(float)
# Total rainfall for the summer months
rainfall_df["Total"] = rainfall_df[months].sum(axis=1)
# Get the year with the maximum rainfall
rainfall_df.sort_values(by="Total", ascending=False, inplace=True)
rainfall_df.reset_index(drop=True, inplace=True)
max_year = rainfall_df.loc[0, "Year"]


csv_path = os.path.join(data_path, f"water-body-testing-{max_year}.csv")
df = pd.read_csv(csv_path)
# cal exceedance rate
df = df[df['Beach Name'] == beach_name]
ex = df[df['Violation'].str.lower() == 'yes']
rate_2006 = len(ex) / len(df)

print(f"2006 exceedance rate: {rate_2006}")

for year in range(2002, 2021):
    if year == 2006:
        continue
    csv_path = os.path.join(data_path, f"water-body-testing-{year}.csv")
    df = pd.read_csv(csv_path)
    # cal exceedance rate
    df = df[df['Beach Name'] == beach_name]
    ex = df[df['Violation'].str.lower() == 'yes']
    if len(df) == 0: continue
    rate = len(ex) / len(df)
    print(rate) 
    if rate > rate_2006:
        print(f"{year} has a higher exceedance rate than 2006")

