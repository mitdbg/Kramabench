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

average_fatalities = df[df['avrh_mean'] < 30]['fatalities_last'].mean()
print(f"Average fatalities: {average_fatalities}")
average_fatalities - df['fatalities_last'].mean()