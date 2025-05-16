import numpy as np
import pandas as pd

data_path = "./data/biomedical/input/"
dfs = pd.read_excel(data_path+'/1-s2.0-S0092867420301070-mmc3.xlsx', sheet_name=None)
gene_readme = dfs['README']

acetyl_sheet = gene_readme.loc[gene_readme["Description"].str.contains("acetylproteomics", case=False), "Sheet"].to_list()[0]
acetyl_sheet

# Since the sheet is technically a list, the first item gets considered a header and we have to add 1
num_genes = len(dfs[acetyl_sheet])+1
print("Number of genes in acetyl sheet:", num_genes)