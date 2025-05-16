import pandas as pd
import numpy as np
import os

data_path = "./data/legal/input/"
df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Number_of_Reports_by_Type.csv", skiprows=2)
df = df.dropna()
df['Year'] = df['Year'].astype(int)
for col in df.columns[1:]:
    df[col] = df[col].str.replace(',', '').astype(int)
df['total'] = df.iloc[:, 1:].sum(axis=1)
df['Other_pct'] = df['Other '] / df['total']
if df['Other_pct'].max() > 0.5:
    print("Yes")
else:
    print("No")