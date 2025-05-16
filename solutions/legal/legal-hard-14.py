import pandas as pd
import numpy as np
import os

data_path = "./data/legal/input/"

state_df = pd.read_csv(f"{data_path}/new_england_states.csv")
state_data = {}
for state in state_df['Name']:
    state = state.replace(" ", "")
    state_data[state] = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft data/{state}.csv", skiprows=2).dropna()
overall_df = pd.concat(state_data.values(), ignore_index=True).reset_index(drop=True)
overall_df['# of Reports'] = overall_df['# of Reports'].apply(lambda x: x.replace(',', '') if isinstance(x, str) else x).astype(int)
overall_df = overall_df.sort_values(by='# of Reports', ascending=False)
overall_df = overall_df.drop_duplicates(subset=['Metropolitan Area'], keep='first')
print(list(overall_df.head(5)["Metropolitan Area"].values))