import pandas as pd
import os
data_path = "./data/wildfire/input/"
aqi_df = pd.read_csv(f'{data_path}/annual_aqi_by_county_2024.csv')
aqi_df['bad days'] = aqi_df['Unhealthy Days'] + aqi_df['Very Unhealthy Days'] + aqi_df['Hazardous Days']
aqi_df['bad days proportion'] = aqi_df['bad days'] / aqi_df['Days with AQI']
aqi_df_state = aqi_df.groupby(['State']).mean(['bad days proportion']).reset_index()
df_combined = pd.read_csv(f'{data_path}/Wildfire_Acres_by_State.csv')

augmented_df = aqi_df_state.merge(df_combined[['State', 'Total Acres Burned', 'Population']], on='State', how='left')
# Ensure the columns are numeric
augmented_df['bad days proportion'] = pd.to_numeric(augmented_df['bad days proportion'], errors='coerce')
augmented_df['Total Acres Burned'] = pd.to_numeric(augmented_df['Total Acres Burned'], errors='coerce')

# Calculate the correlation
correlation = augmented_df[['bad days proportion', 'Total Acres Burned']].corr().iloc[0, 1]
print(f"Correlation between good day proportion and total acres burned: {correlation}")
