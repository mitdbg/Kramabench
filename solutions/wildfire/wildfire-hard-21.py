import datetime
import json
import pandas as pd
data_path = "./data/wildfire/input/"

def day_of_year_to_month_day(year, day_of_year):
    """Converts the day of the year to month and day.

    Args:
        year: The year.
        day_of_year: The day of the year (1-365 or 1-366 for leap years).

    Returns:
        A tuple containing the month and day, or None if the input is invalid.
    """
    try:
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(day_of_year - 1)
        return date.month, date.day
    except ValueError:
        return None

with open(f'{data_path}/state_abbreviation_to_state.json') as f:
    states = json.load(f)
noaa_fire_data_df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')
noaa_fire_data_df = noaa_fire_data_df.dropna()
housing_index_df = pd.read_csv(f'{data_path}/ZHVI.csv')
noaa_fire_data_q7_df = noaa_fire_data_df[(noaa_fire_data_df['start_year'] >= 2005) & (noaa_fire_data_df['start_year'] <= 2010)]
noaa_fire_data_q7_df['agg_lost_value'] = 0
for idx, fire_row in noaa_fire_data_q7_df.iterrows():
    month, _ = day_of_year_to_month_day(fire_row['start_year'], fire_row['start_day_of_year'])
    formatted_date = f"{fire_row['start_year']}-{int(month):02d}-01"
    price = housing_index_df[housing_index_df['Unnamed: 0'] == formatted_date].iloc[0][states[fire_row['state']]]
    noaa_fire_data_q7_df.at[idx, 'agg_lost_value'] = price * fire_row['prim_threatened_aggregate']

noaa_fire_data_q7_df.groupby('state').agg({
    'agg_lost_value': 'sum',
}).nlargest(3, 'agg_lost_value')