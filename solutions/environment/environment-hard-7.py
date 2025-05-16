import pandas as pd
import os
data_path = "./data/environment/input"
# q7

# What was the difference in bacterial exceedance rates for marine beach samples collected in 2023 between communities with more than 50% environmental justice (EJ) populations and those with less than 25% EJ populations?


# Read the 2023 file
filename_2023 = "water-body-testing-2023.csv"
df_2023 = pd.read_csv(os.path.join(data_path, filename_2023))
df_2023['Beach Name'] = df_2023['Beach Name'].str.lower()
df_2023['Community'] = df_2023['Community'].str.lower()
df_2023['Violation'] = df_2023['Violation'].str.lower()

# Filter for marine beaches
marine_df = df_2023[df_2023['Beach Type Description'] == 'Marine']

#  Read EJ population data
filename_ej_population = "environmental-justice-populations.csv"
ej_population_df = pd.read_csv(os.path.join(data_path, filename_ej_population))
ej_population_df['Municipality'] = ej_population_df['Municipality'].str.lower()

# Filter for beaches in EJ BGs with >50% EJ population
ej_ge_50 = ej_population_df[ej_population_df['Percent of population in EJ BGs'] > 50]

# Filter for beaches in EJ BGs with <25% EJ population
ej_le_25 = ej_population_df[ej_population_df['Percent of population in EJ BGs'] < 25]

# Merge the marine_df with ej_population_df on 'Community' and 'Municipality'
marine_ej_ge_50 = pd.merge(marine_df, ej_ge_50, left_on='Community', right_on='Municipality', how='inner')
marine_ej_le_25 = pd.merge(marine_df, ej_le_25, left_on='Community', right_on='Municipality', how='inner')

exceedance_rate_ge_50 = len(marine_ej_ge_50[marine_ej_ge_50['Violation'] == 'yes']) / len(marine_ej_ge_50) * 100
exceedance_rate_le_25 = len(marine_ej_le_25[marine_ej_le_25['Violation'] == 'yes']) / len(marine_ej_le_25) * 100

print(exceedance_rate_ge_50 - exceedance_rate_le_25)