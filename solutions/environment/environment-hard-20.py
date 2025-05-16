#!/usr/bin/env python
# coding: utf-8
import os
import pandas as pd
import numpy as np

data_path = "./data/environment/input/"

# "query": "In 2015, what are the three most polluted beaches of the city that had the least rainfall in the summer (June, July, August)?",

year = 2015
months = ['Jun','Jul','Aug']
fresh_cities = ["boston", 'chatham', 'amherst', 'ashburnham']

fresh_rains = []
for city in fresh_cities:
    csv_path = os.path.join(data_path, f"monthly_precipitations_{city}.csv")
    df = pd.read_csv(csv_path)
    df = df[["Year"]+months]
    # filter if Year in [2007, 2008, 2009]
    df = df[df['Year'].isin(["2015"])]
    # cast Jun, Jul, Aug to float
    for month in months:
        df[month] = df[month].astype(float)
    # sum per row
    df["Total"] = df[months].sum(axis=1)
    rain_df = df
    rainfall = list(df["Total"].values)
    fresh_rains.append(rainfall[0])
fresh_rains = np.array(fresh_rains)
#fresh_rains = np.mean(fresh_rains, axis=0)
print("Fresh Rainfall:", fresh_rains)
min_index = np.argmin(fresh_rains, axis=0)
min_city = fresh_cities[min_index].capitalize()
print("City with min rainfall:", min_city)



# Load the data
csv_path = f'{data_path}water-body-testing-{year}.csv'
df = pd.read_csv(csv_path)
# Filter records to get Freshwater beaches
df = df[df['Community'] == min_city]
# Split ""Beach Name" with @ and remove the second part
df['Beach Name'] = df['Beach Name'].str.split('@').str[0]

print("Freshwater Beaches:", df['Beach Name'].unique())
print("Freshwater Beaches Count:", len(df['Beach Name'].unique()))

# Group by Beach Name to get the count of records and the count of violations
beaches = df.groupby(['Beach Name']).size().reset_index(name='Count')
# Filter to get only the records with violations
exceedance = df[df['Violation'].str.lower() == 'yes']
exceedance = exceedance.groupby(['Beach Name']).size().reset_index(name='Exceedance')
# Merge the two dataframes to get the count of records and violations
beaches = pd.merge(beaches, exceedance, on='Beach Name', how='left')
beaches['Exceedance'] = beaches['Exceedance'].fillna(0)
# sort the beaches by the exceedance rate
beaches[f'Exceedance Rate {year}'] = beaches['Exceedance'] / beaches['Count']
exceedances = beaches[["Beach Name", f'Exceedance Rate {year}']].sort_values(by=f'Exceedance Rate {year}', ascending=False)
print(exceedances.head(3))




