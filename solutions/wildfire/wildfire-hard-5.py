import pandas as pd
import numpy as np
import geopandas as gpd
data_path = "./data/wildfire/input/"
df_noaa = pd.read_csv(f"{data_path}/noaa_wildfires_monthly_stats.csv", skiprows=3)
df_nifc = pd.read_csv(f"{data_path}/nifc_wildfires.csv", delimiter='\t')

# Convert NIFC fires column to numeric, removing commas
df_nifc['Fires_clean'] = df_nifc['Fires'].str.replace(',', '').astype(int)

# Convert NOAA Date to year and group by year, summing the fires
df_noaa['Year'] = df_noaa['Date'].astype(str).str[:4].astype(int)
noaa_annual = df_noaa.groupby('Year')['Number of Fires'].sum().reset_index()

# Merge the two dataframes
merged_df = pd.merge(
    noaa_annual, 
    df_nifc[['Year', 'Fires_clean']], 
    on='Year',
    how='inner'
)

# Calculate difference (NOAA - NIFC) and take mean
avg_difference = (merged_df['Number of Fires'] - merged_df['Fires_clean']).mean()

# Round to nearest whole number
rounded_difference = round(avg_difference)

print(f"On average, NOAA reports {rounded_difference:,} more fires per year than NIFC")