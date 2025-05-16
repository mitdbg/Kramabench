import numpy as np
import pandas as pd

data_path = "./data/biomedical/input/"
dfs = pd.read_excel(data_path+'/1-s2.0-S0092867420301070-mmc3.xlsx', sheet_name=None)

fdr_df = dfs['F-SS-phospho']
fdr_df[['Gene','FDR.phos']]

# fdr_df.groupby('FDR.phos').mean()
gene_mean = fdr_df.groupby('Gene')['FDR.phos'].mean()
cbx3 = gene_mean['CBX3']

other_genes = fdr_df[fdr_df['Gene'] != 'CBX3']
other = np.mean(other_genes['FDR.phos'])

print("Mean FDR for CBX3:", cbx3)
print("Mean FDR for other genes:", other)
print("Difference in mean FDR:", cbx3 - other)