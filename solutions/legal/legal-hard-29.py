import os
import pandas as pd
data_path = "./data/legal/input/"

# get all filepaths
dir_path = f'{data_path}/csn-data-book-2024-csv/CSVs/State MSA Fraud and Other data'
filenames = os.listdir(dir_path)
filepaths = [os.path.join(dir_path, name) for name in filenames]

# compute the metro area with the max pct. of fraud in its own state
max_fraud_metro_area, max_fraud_report_pct = None, 0.0
for idx, filepath in enumerate(filepaths):
    # extract the dataframe
    df = pd.read_csv(filepath)
    df = df.iloc[1:-4]
    column_names = list(df.iloc[0].to_dict().values())
    df.columns = [col.strip() for col in column_names]
    df = df.iloc[1:]

    # skip states with fewer than 5 metro areas
    if len(df) < 5:
        continue

    # compute pct. of total reports for each metro
    df['# of Reports'] = df['# of Reports'].apply(lambda entry: int(entry.replace(",","")))
    df['fraud_report_pct'] = df['# of Reports'] / df['# of Reports'].sum()
    df.sort_values(['fraud_report_pct'], ascending=False, inplace=True)

    # get largest fraud metro area for this state and its percent of reports
    state_max_fraud_metro_area = df.iloc[0]['Metropolitan Area']
    state_max_fraud_report_pct = df.iloc[0]['fraud_report_pct']
    if max_fraud_metro_area is None or state_max_fraud_report_pct > max_fraud_report_pct:
        max_fraud_metro_area = state_max_fraud_metro_area
        max_fraud_report_pct = state_max_fraud_report_pct

print(max_fraud_metro_area)