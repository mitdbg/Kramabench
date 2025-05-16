import pandas as pd
import numpy as np
import geopandas as gpd
data_path = "./data/wildfire/input/"
df_human = pd.read_csv(f"{data_path}/nifc_human_caused_acres.csv", delimiter='\t')
df_lightning = pd.read_csv(f"{data_path}/nifc_lightning_caused_acres.csv", delimiter='\t')

# Combine human and lightning caused fires
# Clean column names by removing asterisks
df_human.columns = df_human.columns.str.replace('*', '')
df_lightning.columns = df_lightning.columns.str.replace('*', '')

# Get geographic columns (exclude Year and Total)
geo_cols = [col for col in df_human.columns if col not in ['Year', 'Total']]

# Convert to numeric, replacing 'N/A' with nan and removing commas
for col in geo_cols:
    df_human[col] = pd.to_numeric(df_human[col].replace('N/A', np.nan).str.replace(',', ''))
    df_lightning[col] = pd.to_numeric(df_lightning[col].replace('N/A', np.nan).str.replace(',', ''))

# Sum the dataframes
df_total = df_human.copy()
for col in geo_cols:
    df_total[col] = df_human[col] + df_lightning[col]
    
# Calculate z-score for each geographic area and year
anomalies = pd.DataFrame()
anomalies['Year'] = df_total['Year']

for col in geo_cols:
    mean = df_total[col].mean()
    std = df_total[col].std()
    anomalies[col] = (df_total[col] - mean) / std

# Find the most extreme z-score
# Use abs() to consider both positive and negative anomalies
max_anomaly = float('-inf')
max_area = ''
max_year = None
max_actual = None
max_mean = None

for col in geo_cols:
    abs_anomalies = abs(anomalies[col])
    max_idx = abs_anomalies.idxmax()
    if abs_anomalies[max_idx] > max_anomaly:
        max_anomaly = abs_anomalies[max_idx]
        max_area = col
        max_year = df_total.loc[max_idx, 'Year']
        max_actual = df_total.loc[max_idx, col]
        max_mean = df_total[col].mean()

area, year, actual, mean, z_score = max_area, max_year, max_actual, max_mean, max_anomaly

print(f"Most anomalous year was {year} in {area}")
print(f"Acres burned: {actual:,.0f}")
print(f"Historical average: {mean:,.0f}")
print(f"Z-score: {z_score:.2f}")
print(f"This was {abs(z_score):.2f} standard deviations from the mean")