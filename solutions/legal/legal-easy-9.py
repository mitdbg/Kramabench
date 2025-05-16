import pandas as pd
import numpy as np
import os

data_path = "./data/legal/input/"
df = pd.read_csv(f'{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Count.csv', skiprows=2)
df = df.dropna()
df['Year'] = df['Year'].astype(int)
df['# of Reports'] = df['# of Reports'].str.replace(',', '').astype(int)
df['diff'] = df['# of Reports'].diff()
df['rel_diff'] = df['diff'] / df['# of Reports'].shift(1)
max_rel_diff_year = df.loc[df['rel_diff'].idxmax(), 'Year']
print(max_rel_diff_year)