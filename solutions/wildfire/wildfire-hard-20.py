# Setup
import pandas as pd
data_path = "./data/wildfire/input/"
noaa_fire_data_df = pd.read_csv(f'{data_path}/noaa_wildfires.csv')
# Q6
noaa_fire_data_2008_df = noaa_fire_data_df[noaa_fire_data_df['control_year'] == 2008]
noaa_fire_data_2008_sorted_df = noaa_fire_data_2008_df.sort_values(by='prim_threatened_aggregate', ascending=False)
total_damage = noaa_fire_data_2008_sorted_df['prim_threatened_aggregate'].sum()
damage_threshold = int(total_damage * 0.9)
cur_agg = 0
result_idx = 0
for idx, fire_row in noaa_fire_data_2008_sorted_df.iterrows():
    cur_agg += fire_row["prim_threatened_aggregate"]
    if cur_agg >= damage_threshold:
        result_idx = idx
        break
print(f"The percentage of wildfires accounting for 90% of residential house damage in 2008 is {result_idx/len(noaa_fire_data_2008_df)}%")