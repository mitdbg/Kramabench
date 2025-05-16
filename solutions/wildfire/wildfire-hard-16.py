# Setup
import pandas as pd
import scipy.stats as stats
# Read the CSV file
data_path = "./data/wildfire/input/"
df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')

# Convert start_date to datetime
df['start_date'] = pd.to_datetime(df['start_date'])

# Filter for January, February, and March
winter_fires = df[df['start_date'].dt.month.isin([1, 2, 3])]

# Filter for known causes (exclude 'U' for unknown)
winter_fires = winter_fires[winter_fires['cause'] != 'U']

# Create contingency table of regions and causes
contingency = pd.crosstab(winter_fires['region'], winter_fires['cause'])

# Perform chi-square test
chi2, p_value = stats.chi2_contingency(contingency)[:2]

# Statistical significance threshold (common value is 0.05)
is_different = p_value < 0.05

print("Contingency table of fire causes by region:")
print(contingency)
print(f"\nChi-square statistic: {chi2:.3f}")
print(f"P-value: {p_value:.3f}")
print(f"Answer: {'Yes' if is_different else 'No'}")