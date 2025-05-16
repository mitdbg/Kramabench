import pandas as pd
import numpy as np
import geopandas as gpd
data_path = "./data/wildfire/input/"
df_costs = pd.read_csv(f"{data_path}/nifc_suppression_costs.csv", delimiter='\t')
df_acres = pd.read_csv(f"{data_path}/nifc_human_caused_acres.csv", delimiter='\t')

# Clean and convert acres data
df_acres['Total_clean'] = df_acres['Total'].str.replace(',', '').astype(float)

# Clean and convert costs data
df_costs['Total_clean'] = df_costs['Total'].str.replace('$', '').str.replace(',', '').astype(float)

# Merge the two dataframes on Year
merged_df = pd.merge(df_acres, df_costs, on='Year')

# Calculate cost per acre
merged_df['cost_per_acre'] = merged_df['Total_clean_y'] / merged_df['Total_clean_x']

# Find the year with highest cost per acre
max_cost_year = merged_df.loc[merged_df['cost_per_acre'].idxmax()]

# Format the output
print(f"Year with highest suppression cost per acre: {max_cost_year['Year']}")
print(f"Cost per acre: ${max_cost_year['cost_per_acre']:.2f}")
print(f"Total acres burned: {max_cost_year['Total_clean_x']:,.0f}")
print(f"Total suppression cost: ${max_cost_year['Total_clean_y']:,.2f}")