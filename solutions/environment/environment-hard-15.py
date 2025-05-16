#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input/"


# ### Query: Which fresh water beach is the most polluted since 2020 (inclusive)? Most polluted is defined as highest average exceedance rate since 2020, and only consider the beaches that are measured in all the years from 2020 to 2023 (inclusive).
# Answer: 

# Load the data
dfs = []
start_year = 2020
end_year = 2024
for year in range(start_year, end_year):
    csv_path = f'{data_path}water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)
    # Filter records to get Freshwater beaches
    df = df[df['Beach Type Description'] == "Fresh"]
    # Split ""Beach Name" with @ and remove the second part
    df['Beach Name'] = df['Beach Name'].str.split('@').str[0]
    
    # Group by Beach Name to get the count of records and the count of violations
    samples = df.groupby(['Beach Name']).size().reset_index(name='Count')
    # Filter to get only the records with violations
    exceedance = df[df['Violation'].str.lower() == 'yes']
    exceedance = exceedance.groupby(['Beach Name']).size().reset_index(name='Exceedance')
    # Merge the two dataframes to get the count of records and violations
    beaches = pd.merge(samples, exceedance, on='Beach Name', how='left')
    beaches[f'Exceedances {year}'] = beaches['Exceedance'].fillna(0)
    beaches[f'Samples {year}'] = samples['Count']
    # sort the beaches by the exceedance rate
    beaches[f'Exceedance Rate {year}'] = beaches['Exceedance'] / beaches['Count']
    beaches = beaches.sort_values(by=f'Exceedance Rate {year}', ascending=False)
    beaches = beaches[["Beach Name", f'Samples {year}', f'Exceedances {year}', f'Exceedance Rate {year}']]
    dfs.append(beaches)




# Join a list of dataframes on "Beach Name"
df = dfs[0]
for d in dfs[1:]:
    df = df.merge(d, on='Beach Name')

df.fillna(0, inplace=True)

# by row, get the average 
cols = [f'Exceedance Rate {year}' for year in range(start_year, end_year)]
df["Avg Rate"] = df[cols].mean(axis=1)
# Sort df by "Ave Rate"
df = df.sort_values(by="Avg Rate", ascending=False)
print(df.head(1)["Beach Name"])




