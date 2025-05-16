import pandas as pd

data_path = "./data/wildfire/input/"
df = pd.read_csv(f"{data_path}/noaa_wildfires_monthly_stats.csv", skiprows=3)

df = df.sort_values('Date')
    
# Create a function to check if dates are consecutive months
def are_consecutive(date1, date2):
    year1, month1 = divmod(date1, 100)
    year2, month2 = divmod(date2, 100)

    # Convert to total months
    total_months1 = year1 * 12 + month1
    total_months2 = year2 * 12 + month2

    return total_months2 - total_months1 == 1

# Create a column called "AbsMonth" to store the absolute month number
df['AbsMonth'] = df['Date'].apply(lambda x: int(str(x)[:4]) * 12 + int(str(x)[4:6]))

max_acres = 0
max_period = None

# Iterate through possible 3-month periods
period_acres_list = []
for i in range(len(df) - 2):
    # Check if months are consecutive
    if df['AbsMonth'].iloc[i] == df['AbsMonth'].iloc[i+1]-1 and df['AbsMonth'].iloc[i+1] == df['AbsMonth'].iloc[i+2]-1:
        period_acres = df['Acres Burned'].iloc[i:i+3].sum()
        period_acres_list.append(period_acres)
        # Update maximum if this period is larger
        if period_acres > max_acres:
            max_acres = period_acres
            max_period = df.iloc[i:i+3]

print({
    'Start Date': max_period['Date'].iloc[0],
    'End Date': max_period['Date'].iloc[-1],
    'Total Acres Burned': max_acres,
    'Period Data': max_period
})