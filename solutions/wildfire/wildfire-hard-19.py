# Setup
import pandas as pd

import datetime
import pytz
import timezonefinder
data_path = "./data/wildfire/input/"

tf = timezonefinder.TimezoneFinder()
def get_timezone(lat, lng):
    return tf.timezone_at(lat=lat, lng=lng)
weather_data_df = pd.read_csv(f'{data_path}/WeatherEvents_Jan2016-Dec2022.csv')
weather_data_2016_df = weather_data_df[weather_data_df['StartTime(UTC)'].str.startswith('2016')]
def convert_starttime_utc_to_local(row):
    utc_time = pd.to_datetime(row['StartTime(UTC)'], utc=True)
    local_timezone = pytz.timezone(row['TimeZone'])
    # local_time = datetime.datetime(utc_time, tzinfo=local_timezone)
    local_time = utc_time.astimezone(local_timezone)
    return local_time


weather_data_2016_df['StartTime(local)'] = weather_data_2016_df.apply(convert_starttime_utc_to_local, axis=1)

def convert_endtime_utc_to_local(row):
    utc_time = pd.to_datetime(row['EndTime(UTC)'], utc=True)
    local_timezone = pytz.timezone(row['TimeZone'])
    # local_time = datetime.datetime(utc_time, tzinfo=local_timezone)
    local_time = utc_time.astimezone(local_timezone)
    return local_time
weather_data_2016_df['EndTime(local)'] = weather_data_2016_df.apply(convert_endtime_utc_to_local, axis=1)

from dateutil import parser
weather_data_2016_df['start_day_of_the_year'] = weather_data_2016_df['StartTime(local)'].apply(lambda x: x.timetuple().tm_yday)
weather_data_2016_df['end_day_of_the_year'] = weather_data_2016_df['EndTime(local)'].apply(lambda x: x.timetuple().tm_yday)

import math
from geopy import distance
noaa_fire_data_df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')
noaa_fire_data_2016_df = noaa_fire_data_df[noaa_fire_data_df['control_year'] == 2016]
noaa_fire_data_2016_df['control_day_previous_day'] = noaa_fire_data_2016_df['control_day_of_year'] - 1
noaa_fire_data_2016_df['rained'] = False


for idx, fire_row in noaa_fire_data_df.iterrows():
    control_day = fire_row['control_day_of_year']
    control_day_prev = control_day - 1

    # Query weather data for matching day or previous day
    weather_matches = weather_data_2016_df.query(
        "(start_day_of_the_year <= @control_day_prev and end_day_of_the_year >= @control_day_prev) or (start_day_of_the_year <= @control_day and end_day_of_the_year >= @control_day)"
    )

    if not weather_matches.empty:
        
        # Do something with each matched weather row
        for _, weather_row in weather_matches.iterrows():
            # Example: extract a field, compute a stat, or store it
            if weather_row['Type'] != "Rain":
                continue
            weather_location = (weather_row['LocationLat'], weather_row['LocationLng'])
            fire_location = (fire_row['latitude'], fire_row['longitude'])
            fire_area_sqkm = fire_row['hec'] / 100
            threshold = math.sqrt(fire_area_sqkm)
            dist_km = distance.distance(weather_location, fire_location).km
            if dist_km <= fire_area_sqkm and weather_row['Precipitation(in)'] > 0.05:
                noaa_fire_data_2016_df.at[idx, 'rained'] = True

q5_percentage = (noaa_fire_data_2016_df['rained'].mean()) * 100
print(f"The percentage of 2016 fire that got under control with the help of a rain is {q5_percentage:.2f}%")
