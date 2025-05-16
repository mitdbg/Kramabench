#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import pathlib

data_path = "./data/environment/input"


rates = []
for year in range(2002, 2024):
    csv_path = f'{data_path}/water-body-testing-{year}.csv'
    df = pd.read_csv(csv_path)
    # Filter records to get Marine beaches
    df = df[df['Beach Type Description'] == "Marine"]
    # Filter to get only the records with violations
    exceedance = df[df['Violation'].str.lower() == 'yes']
    rate = len(exceedance) / len(df)
    rates.append(rate)

average_rate = np.mean(rates)
print(f"Average rate of exceedance from 2002 to 2023: {average_rate:.2%}")


# print rate for each year
for year, rate in zip(range(2002, 2024), rates):
    print(f"Rate of exceedance for {year}: {rate:.2%}")



