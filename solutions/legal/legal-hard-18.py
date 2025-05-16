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
identity_theft_percentage = cat_df[cat_df['Category'] == 'Identity Theft']['Percentage'].values[0]
identity_theft_percentage = float(identity_theft_percentage.strip('%')) / 100

id_theft_age_df = pd.read_csv(f'{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Identity_Theft_Reports_by_Age.csv', skiprows=2)
id_theft_age_df = id_theft_age_df.dropna()
id_theft_age_df['# of Reports'] = id_theft_age_df['# of Reports'].str.replace(',', '').astype(int)
id_theft_age_df['Percentage of reports'] = id_theft_age_df['# of Reports'] / id_theft_age_df['# of Reports'].sum()
id_theft_over_40 = id_theft_age_df[id_theft_age_df['Age Range'] > '40']['Percentage of reports'].sum()

print(int(np.round(total_2007_reports * identity_theft_percentage * id_theft_over_40, -3)))
