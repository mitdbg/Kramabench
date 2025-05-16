import pandas as pd
data_path = "./data/biomedical/input/"
clinical_df = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc1.xlsx")

# First, read the table of case numbers, and filter out the ones that are not excluded 
# Filter out the excluded case
print("Total number of cases:", len(clinical_df))
case_df = clinical_df[clinical_df['Case_excluded'] == 'No']
case_df = case_df[case_df['Histologic_type'].isin(['Endometrioid','Serous'])]
print("Tumor cases:", len(case_df))

tmb_df = pd.read_excel(data_path+'/1-s2.0-S0092867420301070-mmc7.xlsx', sheet_name=["B-APM subtypes"])['B-APM subtypes']
# find the idx where APP_Z_score is max
min_idx = tmb_df.loc[tmb_df['APP_Z_score'].idxmin()]['idx']

# find the idx where APP_Z_score is max
case_df[case_df['idx']==min_idx]['Age']

import numpy as np
serous_df = case_df[case_df['Histologic_type'] == 'Serous']
serous_cases = serous_df['idx'].tolist()
tmb_df = tmb_df[tmb_df['idx'].isin(serous_cases)]
vpm = tmb_df['Log2_variant_per_Mbp'].values
vpm = 2**vpm
np.median(vpm)