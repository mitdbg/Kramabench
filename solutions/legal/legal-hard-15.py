import pandas as pd
import numpy as np
import os
data_path = "./data/legal/input/"

state_data = {}
directory = f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft data"
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    state_data[filename.split('.')[0]] = pd.read_csv(filepath, skiprows=2).dropna()
overall_df = pd.concat(state_data.values(), ignore_index=True).reset_index(drop=True)
overall_df['states'] = overall_df['Metropolitan Area'].apply(lambda x: x.split(',')[1].split()[0] if ',' in x else None)
overall_df["is_cross_state"] = overall_df['states'].apply(lambda x: True if ('-' in x) else False)
overall_df['# of Reports'] = overall_df['# of Reports'].apply(lambda x: x.replace(',', '') if isinstance(x, str) else x).astype(int)
print(overall_df[overall_df['is_cross_state']]['# of Reports'].sum())