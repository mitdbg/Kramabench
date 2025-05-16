import pandas as pd
import os
data_path = "./data/wildfire/input/"
df = pd.read_csv(f'{data_path}/Fire_Weather_Data_2002-2014_2016.csv')
df[df['start_year'] == 2012]

import matplotlib.pyplot as plt

# Ensure 'start_date' is in datetime format
df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')

# Drop rows with invalid or missing 'start_date'
df = df.dropna(subset=['start_date'])

# Plot the histogram
plt.figure(figsize=(10, 6))
df[df['start_year'] == 2016]['start_date'].dt.month.hist(bins=12, edgecolor='black')
plt.title('Histogram of Fire Start Dates by Month')
plt.xlabel('Month')
plt.ylabel('Frequency')
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

from scipy.stats import norm
import numpy as np

# Extract the month data for the histogram
fire_months = df[df['start_year'] == 2004]['start_date'].dt.month

# Fit a Gaussian distribution to the data
mu, sigma = norm.fit(fire_months)

# Print the learned parameters
print(f"Estimated mean (mu): {mu}")
print(f"Estimated standard deviation (sigma): {sigma}")

# Plot the histogram and the fitted Gaussian curve
plt.figure(figsize=(10, 6))
fire_months.hist(bins=12, density=True, alpha=0.6, color='g', edgecolor='black')

# Generate values for the Gaussian curve
x = np.linspace(1, 12, 100)
pdf = norm.pdf(x, mu, sigma)

# Plot the Gaussian curve
plt.plot(x, pdf, 'r-', label=f'Gaussian Fit\n$\mu={mu:.2f}$, $\sigma={sigma:.2f}$')
plt.title('Histogram of Fire Start Dates by Month with Gaussian Fit')
plt.xlabel('Month')
plt.ylabel('Density')
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

years = [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2016]

def retrieve_mu_sigma(df, year):
    fire_months = df[df['start_year'] == year]['start_date'].dt.month
    mu, sigma = norm.fit(fire_months)
    return mu, sigma

# Retrieve mu and sigma for each year
mu_sigma_list = [retrieve_mu_sigma(df, year) for year in years]
mu_sigma_list
# Create a DataFrame for better visualization
mu_sigma_df = pd.DataFrame(mu_sigma_list, columns=['mu', 'sigma'], index=years)
mu_sigma_df
# Plot the mu and sigma values over the years
plt.figure(figsize=(12, 6))
plt.plot(mu_sigma_df.index, mu_sigma_df['mu'], marker='o', label='Mean (mu)')
plt.plot(mu_sigma_df.index, mu_sigma_df['sigma'], marker='o', label='Standard Deviation (sigma)')
plt.title('Mean and Standard Deviation of Fire Start Dates Over the Years')
plt.xlabel('Year')
plt.ylabel('Value')
plt.xticks(mu_sigma_df.index)
plt.legend()
plt.grid()
plt.show()