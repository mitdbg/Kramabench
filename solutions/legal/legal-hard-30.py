import pandas as pd

import os
data_path = "./data/legal/input/"

# get all filepaths
fraud_dir_path = f'{data_path}/csn-data-book-2024-csv/CSVs/State MSA Fraud and Other data'
fraud_filenames = os.listdir(fraud_dir_path)
fraud_filepaths = [os.path.join(fraud_dir_path, name) for name in fraud_filenames]

theft_dir_path = f'{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft Data'
theft_filenames = os.listdir(theft_dir_path)
theft_filepaths = [os.path.join(theft_dir_path, name) for name in theft_filenames]

# compute the number of fraud and identity theft reports in each metro area and return True
# if a metro area has more identity theft reports than fraud reports

# compute mapping from metro area to num fraud reports
metro_area_to_fraud_reports = {}
for idx, filepath in enumerate(fraud_filepaths):
    # extract the dataframe
    df = pd.read_csv(filepath)
    df = df.iloc[1:-4]
    column_names = list(df.iloc[0].to_dict().values())
    df.columns = [col.strip() for col in column_names]
    df = df.iloc[1:]

    # compute pct. of total reports for each metro
    df['# of Reports'] = df['# of Reports'].apply(lambda entry: int(entry.replace(",","")))
    area_to_num_reports = {row['Metropolitan Area']: row['# of Reports'] for _, row in df.iterrows()}
    metro_area_to_fraud_reports = {**area_to_num_reports, **metro_area_to_fraud_reports}

# compute mapping from metro area to num identity theft reports
metro_area_to_identity_reports = {}
for idx, filepath in enumerate(theft_filepaths):
    # extract the dataframe
    df = pd.read_csv(filepath)
    df = df.iloc[1:-4]
    column_names = list(df.iloc[0].to_dict().values())
    df.columns = [col.strip() for col in column_names]
    df = df.iloc[1:]

    # compute pct. of total reports for each metro
    df['# of Reports'] = df['# of Reports'].apply(lambda entry: int(entry.replace(",","")))
    area_to_num_reports = {row['Metropolitan Area']: row['# of Reports'] for _, row in df.iterrows()}
    metro_area_to_identity_reports = {**area_to_num_reports, **metro_area_to_identity_reports}

cnt = 0
for metro_area, num_identity_reports in metro_area_to_identity_reports.items():
    num_fraud_reports = metro_area_to_fraud_reports.get(metro_area, None)
    if num_fraud_reports is not None:
        cnt += 1
    if num_fraud_reports is not None and num_identity_reports > num_fraud_reports:
        print(metro_area)
        print(True)
        break
print(cnt)