#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from scipy.spatial import cKDTree
data_path = "./data/archeology/input/"

roman_path = f"{data_path}/roman_cities.csv"
cities_path = f"{data_path}/worldcities.csv"
roman_df = pd.read_csv(roman_path)
global_df = pd.read_csv(cities_path)

roman_loc = roman_df[["Longitude (X)", "Latitude (Y)"]]
global_df = global_df[global_df["population"] > 100000]
global_loc = global_df[['lng', 'lat']]

tree = cKDTree(roman_loc)
matches = tree.query_ball_point(global_loc.values, r=0.1)

global_indices = list()
for i, match_indices in enumerate(matches):
    if match_indices:
        global_indices.append(i)
answer_df = global_df.iloc[global_indices].reset_index(drop=True)

print(len(answer_df["city"]))

