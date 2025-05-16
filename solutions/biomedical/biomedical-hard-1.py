import pandas as pd
data_path = "./data/biomedical/input/"
clinical_df = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc1.xlsx")
proteomics_dfs = pd.read_excel(data_path+'/1-s2.0-S0092867420301070-mmc2.xlsx', sheet_name= None)

global_df = proteomics_dfs['A-global-proteomics']
phospho_df = proteomics_dfs['B-phospho-proteomics']

# First, read the table of case numbers, and filter out the ones that are not excluded 
# Filter out the excluded case
print("Total number of cases:", len(clinical_df))
case_df = clinical_df[clinical_df['Case_excluded'] == 'No']
case_df = case_df[case_df['Histologic_type'].isin(['Endometrioid','Serous'])]
print("Tumor cases:", len(case_df))

from scipy.stats import spearmanr
import numpy as np

# Filter the global proteomics data for tumor cases 
case_ids = case_df['idx'].tolist()
global_df = global_df.filter(items=case_ids+["idx"], axis=1)
phospho_df = phospho_df.filter(items=case_ids+["idx"], axis=1)

plk1 = global_df[global_df['idx'] == 'PLK1'].values.tolist()[0][:-1]
chek2 = phospho_df[phospho_df['idx'] == 'CHEK2-S163'].values.tolist()[0][:-1]

plk1 = np.asarray(plk1)[~np.isnan(chek2)]
chek2 = np.asarray(chek2)[~np.isnan(chek2)]

# Calculate the Spearman correlation
spearman_corr, p_value = spearmanr(plk1, chek2)
print("Spearman correlation coefficient:", spearman_corr)
print("P-value:", p_value)