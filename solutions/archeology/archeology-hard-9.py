#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from scipy.spatial import cKDTree
import re
data_path = "./data/archeology/input/"

roman_path = f"{data_path}/roman_cities.csv"
cities_path = f"{data_path}/worldcities.csv"

roman_df = pd.read_csv(roman_path)
global_df = pd.read_csv(cities_path)
global_df = global_df[global_df["population"] > 1000000]

def clean_rank(s):
    numbers = re.findall(r'\d+\.?\d*', s)
    numbers = list(map(float, numbers))
    return sum(numbers) / len(numbers) if len(numbers) > 0 else -1

roman_df["Barrington Atlas Rank"] = roman_df["Barrington Atlas Rank"].apply(clean_rank)

roman_loc = roman_df[["Longitude (X)", "Latitude (Y)"]]
global_loc = global_df[['lng', 'lat']]

tree = cKDTree(roman_loc)
matches = tree.query_ball_point(global_loc.values, r=0.1)

global_indices = list()
roman_indices = list()
for i, match_indices in enumerate(matches):
    if match_indices:
        global_indices.append(i)
        max_rank_city = roman_df.iloc[match_indices]["Barrington Atlas Rank"].idxmax()
        roman_indices.append(max_rank_city)

pop_df = global_df.iloc[global_indices].reset_index(drop=True)["population"]
rank_df = roman_df.iloc[roman_indices].reset_index(drop=True)["Barrington Atlas Rank"]

r = pop_df.corr(rank_df)
print(round(r, 6))