import pandas as pd
import numpy as np
import os

data_path = "./data/legal/input/"

state_data = {}
directory = f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft data"
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    state_name = filename.split('.')[0]
    state_data[state_name] = pd.read_csv(filepath, skiprows=2).dropna()
    state_data[state_name]['state_name'] = state_name
overall_df = pd.concat(state_data.values(), ignore_index=True).reset_index(drop=True)
overall_df['# of Reports'] = overall_df['# of Reports'].apply(lambda x: x.replace(',', '') if isinstance(x, str) else x).astype(int)
overall_df = overall_df.groupby('state_name').filter(lambda x: len(x) > 1)
overall_df['fraction_of_state'] = overall_df['# of Reports'] / overall_df.groupby('state_name')['# of Reports'].transform('sum')
print(overall_df.sort_values(by='fraction_of_state', ascending=False).iloc[0]['state_name'])