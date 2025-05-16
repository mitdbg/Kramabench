# Setup
import pandas as pd
data_path = "./data/wildfire/input/"
noaa_fire_data_df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')
# Data cleaning
import numpy as np
noaa_fire_data_df['dominant_strategy_25_indicator'] = np.where(noaa_fire_data_df['dominant_strategy_25_s'] == "Full Suppression", 1, 0)
noaa_fire_data_df['dominant_strategy_50_indicator'] = np.where(noaa_fire_data_df['dominant_strategy_50_s'] == "Full Suppression", 1, 0)
noaa_fire_data_df['dominant_strategy_75_indicator'] = np.where(noaa_fire_data_df['dominant_strategy_75_s'] == "Full Suppression", 1, 0)

import statsmodels.api as sm
noaa_fire_data_df = noaa_fire_data_df.dropna()
y = noaa_fire_data_df['duration']
x_25 = noaa_fire_data_df[['dominant_strategy_25_indicator', 'avrh_mean', 'wind_med', 'erc_med', 'rain_sum', 'hec']]
x_25 = sm.add_constant(x_25)
model = sm.OLS(y, x_25).fit(cov_type='HC3')
print(model.summary())

x_50 = noaa_fire_data_df[['dominant_strategy_50_indicator', 'avrh_mean', 'wind_med', 'erc_med', 'rain_sum', 'hec']]
x_50 = sm.add_constant(x_50)
model = sm.OLS(y, x_50).fit(cov_type='HC3')
print(model.summary())

x_75 = noaa_fire_data_df[['dominant_strategy_75_indicator', 'avrh_mean', 'wind_med', 'erc_med', 'rain_sum', 'hec']]
x_75 = sm.add_constant(x_75)
model = sm.OLS(y, x_75).fit(cov_type='HC3')
print(model.summary())

y_2 = noaa_fire_data_df['prim_threatened_aggregate']
model = sm.OLS(y_2, x_25).fit(cov_type='HC3')
print(model.summary())
model = sm.OLS(y_2, x_50).fit(cov_type='HC3')
print(model.summary())
model = sm.OLS(y_2, x_75).fit(cov_type='HC3')
print(model.summary())