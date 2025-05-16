import pandas as pd
data_path = "./data/wildfire/input/"
noaa_fire_data_df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')

noaa_fire_july = noaa_fire_data_df[(noaa_fire_data_df['start_day_of_year'] >= 181) & (noaa_fire_data_df['start_day_of_year'] < 213)]
correlation = noaa_fire_july['wind_med'].corr(noaa_fire_july['hec'])
print(f"The correlation coefficient is {correlation}")
# The correlation is not strong