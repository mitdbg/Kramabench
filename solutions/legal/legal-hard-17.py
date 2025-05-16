import pandas as pd
import numpy as np
import os
data_path = "./data/legal/input/"

df = pd.read_csv(f'{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Count.csv', skiprows=2)
df = df.dropna()
df['Year'] = df['Year'].astype(int)
df['# of Reports'] = df['# of Reports'].str.replace(',', '').astype(int)
total_2007_reports = df[df['Year'] == 2007]['# of Reports'].values[0]

cat_df = pd.read_csv(f'{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Categories.csv', skiprows=2, encoding="unicode_escape")
cat_df = cat_df.dropna()
auto_related_percentage = cat_df[cat_df['Category'] == 'Auto Related']['Percentage'].values[0]
auto_related_percentage = float(auto_related_percentage.strip('%')) / 100
print(int(np.round(auto_related_percentage * total_2007_reports)))