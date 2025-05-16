import pandas as pd
import os
data_path = "./data/wildfire/input/"
df_combined = pd.read_csv(f'{data_path}/Wildfire_Acres_by_State.csv')
df_combined['acres per capita'] = df_combined['Total Acres Burned'] / df_combined['Population']
df_combined.loc[df_combined['acres per capita'].idxmax()]