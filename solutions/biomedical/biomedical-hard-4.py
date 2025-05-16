import pandas as pd
data_path = "./data/biomedical/input/"
clinical_df = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc1.xlsx")
peptide_dfs = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc4.xlsx", sheet_name=None)

peptide_df = pd.concat([peptide_dfs[key] for key in peptide_dfs if key!='README'], ignore_index=True)

hpk_case = peptide_df[peptide_df['Peptide'] == 'HPKPEVLGSSADGALLVSLDGLR']
samples = hpk_case['Samples_With_Peptide'].values
print("Samples with peptide:", samples)

# Cast the samples to a list, and split by comma
sample_ids = [sample.strip() for sample in samples[0].split(',')]

# Fetch the clinical data for the samples
samples_df = clinical_df[clinical_df['idx'].isin(sample_ids)]
# Filter the samples_df to get the tumor stage
answer = list(samples_df['Histologic_Grade_FIGO'].unique())
print("Grade of tumors with peptide HPKPEVLGSSADGALLVSLDGLR:", answer)