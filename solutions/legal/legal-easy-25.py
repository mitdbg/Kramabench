import os
import pandas as pd

data_path = "./data/legal/input/"
military_consumer_fraud_df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Fraud, Identity Theft, and Other Reports by Military Consumers.csv")

# extract branch fraud table
branch_fraud_df = military_consumer_fraud_df.iloc[7:14]
column_names = list(branch_fraud_df.iloc[0].to_dict().values())
branch_fraud_df.columns = column_names
branch_fraud_df = branch_fraud_df.iloc[1:]

# find branch w/max median fraud loss
max_branch, max_median_fraud_loss = None, None
for idx, branch_row in branch_fraud_df.iterrows():
    median_fraud_loss = int(branch_row['Median Fraud Loss'].replace("$","").replace(",",""))
    if max_branch is None or median_fraud_loss > max_median_fraud_loss:
        max_branch = branch_row['Military Branch']
        max_median_fraud_loss = median_fraud_loss
print(max_branch)