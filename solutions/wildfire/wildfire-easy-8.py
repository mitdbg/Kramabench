import pandas as pd
import os

data_path = "./data/wildfire/input/"
file_path = f'{data_path}/Fire_Weather_Data_2002-2014_2016.csv'
if os.path.exists(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Display the first few rows of the DataFrame
    print(df.head())

    # Display the shape of the DataFrame
    print(f"DataFrame shape: {df.shape}")

    # Display the columns of the DataFrame
    print(f"DataFrame columns: {df.columns.tolist()}")

    # Display the data types of each column
    print(f"Data types:\n{df.dtypes}")
    # Display the number of missing values in each column
    print(f"Missing values:\n{df.isnull().sum()}")
else:
    print(f"File not found: {file_path}")
# Check for duplicates
duplicates = df.duplicated().sum()
print(f"Number of duplicate rows: {duplicates}")
# Check for unique values in the 'State' column
unique_states = df['state'].unique()
print(f"Unique states: {unique_states}")
# Check the number of unique values in the 'State' column
unique_state_count = df['state'].nunique()
print(f"Number of unique states: {unique_state_count}")
# Check the number of unique values in the 'station_verified_in_psa' column
unique_stations = df['station_verified_in_psa'].unique()
print(f"Unique fire weather stations: {unique_stations}")
# Check the number of unique values in the 'station_verified_in_psa' column
unique_station_count = df['station_verified_in_psa'].nunique()
print(f"Number of unique fire weather stations: {unique_station_count}")

df['acres'] = df['hec'] * 2.741

# Group the data by 'cause' for rows where 'acres' > 100 and count the occurrences
grouped_table = df[df['acres'] > 100].groupby(['cause']).size().reset_index(name='count')

# Display the table
print(grouped_table)