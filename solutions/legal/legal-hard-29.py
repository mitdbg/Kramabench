import os
import pandas as pd
data_path = "./data/legal/input/"

# get all filepaths (Puerto Rico is a territory, not a state)
dir_path = f'{data_path}/csn-data-book-2024-csv/CSVs/State MSA Fraud and Other data'
filenames = [name for name in os.listdir(dir_path) if name != 'PuertoRico.csv']
filepaths = [os.path.join(dir_path, name) for name in filenames]

state_data = {}
for fpath in filepaths:
    if 'PuertoRico' in fpath or 'Columbia' in fpath:
        continue
    filename = os.path.basename(fpath)
    df = pd.read_csv(fpath, skiprows=2).dropna()
    df['# of Reports'] = df['# of Reports'].apply(lambda x: x.replace(',', '') if isinstance(x, str) else x).astype(int)
    state_data[filename.split('.')[0]] = df

areas_pct = {}
valid_states = {state: df for state, df in state_data.items() if len(df) >= 5}

all_reports = []
all_pct = []
for state, df in valid_states.items():
    df['states'] = df['Metropolitan Area'].apply(lambda x: x.split(',')[1].split()[0] if ',' in x else None)
    df["is_cross_state"] = df['states'].apply(lambda x: True if ('-' in x) else False)
    df['fraud_report_pct'] = df['# of Reports'] / df['# of Reports'].sum()
    all_reports.extend(df['# of Reports'].tolist())
    all_pct.extend(df['fraud_report_pct'].tolist())
    single_state_df = df[~df['is_cross_state']].copy()
    single_state_df.sort_values(['fraud_report_pct'], ascending=False, inplace=True)
    area = single_state_df.iloc[0]['Metropolitan Area']
    areas_pct[area] = single_state_df.iloc[0]['fraud_report_pct']

sorted_areas = sorted(areas_pct.items(), key=lambda x: x[1], reverse=True)
max_fraud_metro_area, max_fraud_report_pct = sorted_areas[0]
print(max_fraud_metro_area)