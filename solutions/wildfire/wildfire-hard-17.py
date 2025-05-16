# Setup
import pandas as pd
data_path = "./data/wildfire/input/"
# Read both CSV files
fires_df = pd.read_csv(f'{data_path}/noaa_wildfires_sylvia.csv')
stations_df = pd.read_csv(f'{data_path}/PublicView_RAWS_-3515561676727363726.csv')

# Get unique station IDs used in fire monitoring
used_stations = fires_df['station_verified_in_psa'].unique()

# Convert 'NWS ID' to integer type, handling any errors
stations_df['NWS ID'] = pd.to_numeric(stations_df['NWS ID'], errors='coerce')

# Filter stations that were used in fire monitoring
used_station_data = stations_df[stations_df['NWS ID'].isin(used_stations)]

# Calculate mean elevation, dropping any NaN values
mean_elevation = used_station_data['Elevation'].dropna().mean()

print(f"Number of unique stations used in fire monitoring: {len(used_stations)}")
print(f"Number of stations found with elevation data: {len(used_station_data)}")
print(f"Average elevation: {mean_elevation:.1f} feet")