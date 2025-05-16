import pandas as pd
import numpy as np
import os

data_path = "./data/legal/input/"
cat_df = pd.read_csv(f'{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Categories.csv', skiprows=2, encoding="unicode_escape")
cat_df = cat_df.dropna()
cat_df[' # of Reports '] = cat_df[' # of Reports '].str.replace(',', '').astype(int)
print((cat_df[" # of Reports "].max() / cat_df[" # of Reports "].min()).round(2))