import pandas as pd
import numpy as np
import geopandas as gpd
data_path = "./data/wildfire/input/"
df_noaa = pd.read_csv(f"{data_path}/noaa_wildfires_monthly_stats.csv", skiprows=3)
df_nifc = pd.read_csv(f"{data_path}/nifc_wildfires.csv", delimiter='\t')

# Clean NIFC data
df_nifc['Fires_clean'] = df_nifc['Fires'].str.replace(',', '').astype(int)
df_nifc['Acres_clean'] = df_nifc['Acres'].str.replace('*', '', regex=False).str.replace(',', '').astype(int)

# Convert NOAA Date to year and group by year, summing both fires and acres
df_noaa['Year'] = df_noaa['Date'].astype(str).str[:4].astype(int)
noaa_annual = df_noaa.groupby('Year').agg({
    'Number of Fires': 'sum',
    'Acres Burned': 'sum'
}).reset_index()

# Merge the two dataframes
merged_df = pd.merge(
    noaa_annual, 
    df_nifc[['Year', 'Fires_clean', 'Acres_clean']], 
    on='Year',
    how='inner'
)

# Calculate differences
merged_df['fire_difference'] = merged_df['Number of Fires'] - merged_df['Fires_clean']
merged_df['acres_difference'] = merged_df['Acres Burned'] - merged_df['Acres_clean']

# Calculate correlation
correlation = merged_df['fire_difference'].corr(merged_df['acres_difference'])

print(f"Correlation coefficient: {correlation:.3f}")