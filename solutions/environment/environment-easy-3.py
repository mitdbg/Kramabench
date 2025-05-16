import pandas as pd
import os
data_path = "./data/environment/input"

# q3

# How many beaches had a higher exceedance rate for water samples collected in 2013 compared to 2012, excluding those with no samples in 2012?

# Read the 2013 file
filename_2013 = "water-body-testing-2013.csv"
filename_2012 = "water-body-testing-2012.csv"
df_2013 = pd.read_csv(os.path.join(data_path, filename_2013))
df_2013['Beach Name'] = df_2013['Beach Name'].str.lower()

# Read the 2012 file
filename_2012 = "water-body-testing-2012.csv"
df_2012 = pd.read_csv(os.path.join(data_path, filename_2012))
df_2012['Beach Name'] = df_2012['Beach Name'].str.lower()

# Compute the number of samples, number of violations, and the exceedance rate (its ratio) for 2013 for each beach

# Group by beach name and compute samples and violations for 2013
beach_agg_2013 = df_2013.groupby('Beach Name').agg({
    'Beach Name': 'count',  # Total samples
    'Violation': lambda x: (x.str.lower() == 'yes').sum()  # Count of violations
}).rename(columns={
    'Beach Name': 'total_samples',
    'Violation': 'num_violations'
})

# Calculate exceedance rate for each beach in 2013
beach_agg_2013['exceedance_rate'] = (beach_agg_2013['num_violations'] / beach_agg_2013['total_samples']) * 100

# Compute the number of samples, number of violations, and the exceedance rate (its ratio) for 2012 for each beach

# Group by beach name and compute samples and violations for 2012
beach_agg_2012 = df_2012.groupby('Beach Name').agg({
    'Beach Name': 'count',  # Total samples
    'Violation': lambda x: (x.str.lower() == 'yes').sum()  # Count of violations
}).rename(columns={
    'Beach Name': 'total_samples',
    'Violation': 'num_violations'
})

# Calculate exceedance rate for each beach in 2012
beach_agg_2012['exceedance_rate'] = (beach_agg_2012['num_violations'] / beach_agg_2012['total_samples']) * 100

# Find the beaches that had a higher exceedance rate in 2013 compared to 2012
# Inner join the 2012 and 2013 data on beach name
beaches_comparison = pd.merge(
    beach_agg_2012,
    beach_agg_2013,
    left_index=True,
    right_index=True,
    suffixes=('_2012', '_2013')
)
beaches = beaches_comparison[beaches_comparison['exceedance_rate_2013'] > beaches_comparison['exceedance_rate_2012']]
print(len(beaches))
