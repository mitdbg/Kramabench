import os
import pandas as pd

data_path = "./data/legal/input/"
df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_State_Top_Ten_Report_Categories.csv")

# extract data
df = df.iloc[1:-4]
column_names = list(df.iloc[0].to_dict().values())
df.columns = [col.strip() for col in column_names]
df = df.iloc[1:]

# group by state, sort by # reports, and add to list of states w/Identity Theft as top category
identity_theft_states = []
for state, state_df in df.groupby('State'):
    state_df['# of Reports'] = state_df['# of Reports'].apply(lambda entry: int(entry.replace(",","")))
    state_df.sort_values(['# of Reports'], ascending=False, inplace=True)
    if state_df.iloc[0]['Category'] == 'Identity Theft':
        identity_theft_states.append(state)

print(sorted(identity_theft_states))