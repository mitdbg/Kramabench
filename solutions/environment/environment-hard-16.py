#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"



#What are the marine beaches (from 2002 to 2023) remained safe to swimming for the entire time (i.e., no violation at all throughout the seasons)?
dfs = []
for year in range(2002, 2024):
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)
    df = df[df['Beach Type Description'] == "Marine"]
    # Split ""Beach Name" with @ and remove the second part
    df['Beach Name'] = df['Beach Name'].str.split('@').str[0]
    # find beaches with no violations
    df["Violation"] = df['Violation'].str.lower()
    df = df[['Beach Name', 'Violation']]
    # Append df 
    dfs.append(df)
total_df = pd.concat(dfs)



beaches = total_df['Beach Name'].unique()
print(f"Total number of uinque beaches: {len(beaches)}")
ex_beaches = total_df[total_df['Violation'] == 'yes']['Beach Name'].unique()


print(f"Total number of unique beaches with violations: {len(ex_beaches)}")


# Intersect beaches and ex_beaches
safe_beaches = [b for b in beaches if b not in ex_beaches]


print(len(safe_beaches))




