import pandas as pd
import os
data_path = "./data/environment/input"

# q2

# Between 2002 and 2023 (inclusive), which years had a bacterial exceedance rate in water samples collected from freshwater beaches higher than the average freshwater beach exceedance rate?

all_years = list(range(2002, 2024))

years_exceedance_rate = {}

total_samples = 0
total_violations = 0
# Read all the files, compute the exceedance rate for each year for freshwater beaches.
for year in all_years:
    filename = f"water-body-testing-{year}.csv"
    df = pd.read_csv(os.path.join(data_path, filename))
    fresh_df = df[df['Beach Type Description'].str.lower() == 'fresh']
    violation_fresh_df = fresh_df[fresh_df['Violation'].str.lower() == 'yes']
    total_samples += len(fresh_df)
    total_violations +=len(violation_fresh_df)
    years_exceedance_rate[year] = len(violation_fresh_df) / len(fresh_df) * 100.0

# Compute the historical average exceedance rate
historical_average_exceedance_rate = total_violations / total_samples * 100.0

# Find the years where the exceedance rate is higher than the historical average
years_exceedance_rate_higher_than_historical_average = [year for year, exceedance_rate in years_exceedance_rate.items() if exceedance_rate > historical_average_exceedance_rate]
print(years_exceedance_rate_higher_than_historical_average)