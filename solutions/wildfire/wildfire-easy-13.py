import pandas as pd
import os
data_path = "./data/wildfire/input/"
# import ace_tools as tools; tools.display_dataframe_to_user(name="Cleaned Helicopter Requests by Region", dataframe=df_cleaned)
df_cleaned = pd.read_csv(f'{data_path}/cleaned_helicopter_requests_by_region.csv')

df_cleaned.loc[df_cleaned['Total Helicopter Requests'].idxmax()]