#!/usr/bin/env python
# coding: utf-8
import pandas as pd
data_path = "./data/archeology/input/"

city_path = f"{data_path}/worldcities.csv"
df = pd.read_csv(city_path)

# Filter for rows where country is not nan
df = df[df["population"].notna()]
countries = df.groupby("country")["population"].mean()
index = countries.idxmax()
print(index)



