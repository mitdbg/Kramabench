# "Which protein are found to be hyperactivated in CNV-high endometroid samples?"
import pandas as pd
data_path = "./data/biomedical/input/"

clinical_df = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc1.xlsx")
hyperactivated_df = pd.read_csv(data_path+"/hyperactivated.csv")
phospho_drugs = pd.read_excel(data_path+"/1-s2.0-S0092867420301070-mmc6.xlsx", sheet_name=None)
drugs_df = phospho_drugs['G-FDA approved drugs']

# Find endometrioid samples with CNV-high
cnv_df = clinical_df[clinical_df['CNV_class'] == 'CNV_HIGH']
endo_df = cnv_df[cnv_df['Histologic_type'] == 'Endometrioid']
endo_df = endo_df[endo_df['Case_excluded'] == 'No']
endo_samples = endo_df['idx'].tolist()
print("Endometrioid samples in CNV-high group:", endo_samples)

# find hyperactivated proteins in phosphoproteomics data
hyperactivated_df = hyperactivated_df[hyperactivated_df['sample_id'].isin(endo_samples)]
unique_proteins = hyperactivated_df['protein'].unique().tolist()
print("Unique proteins hyperactivated in CNV-high endometrioid samples:", unique_proteins)

# Find the unique drugs that target these proteins
targeted_proteins = drugs_df[drugs_df['gene_name'].isin(unique_proteins)]['gene_name'].unique().tolist()
print("Targeted proteins in CNV-high endometrioid samples:", targeted_proteins)