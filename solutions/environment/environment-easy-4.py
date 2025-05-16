#!/usr/bin/env python
# coding: utf-8


import os
import pandas as pd
import numpy as np
import pathlib

data_path = "../../data/environment/"


# ### Query: What is the percentage of time in 2019-2023 that the water quality at Quincy's Wollaston Beach has met swimming standards? 

years = [2019, 2020, 2021, 2022, 2023]
# Load the data
rates = []
for year in years:
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)
    # Filter records to get Beach Name has "Wollaston"
    df = df[df['Beach Name'].str.contains("Wollaston", na=False)]
    print(df['Beach Name'].unique())
    # set the violation column to lower case
    exceedance = df[df['Violation'].str.lower() == 'yes']
    exceedance_rate = len(exceedance) / len(df) if len(df) > 0 else 0
    rates += [exceedance_rate]
    print(f"Loaded {len(df)} records from {csv_path}")

print(rates)
avg_rate = 1 - np.mean(rates)
print(f"The percentage of time in 2019-2023 that the beach was open is {avg_rate:.1%}")




