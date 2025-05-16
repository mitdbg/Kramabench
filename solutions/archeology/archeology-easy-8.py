#!/usr/bin/env python
# coding: utf-8
import pandas as pd
data_path = "./data/archeology/input/"

roman_path = f"{data_path}/roman_cities.csv"
roman_df = pd.read_csv(roman_path)

filtered_df = roman_df[roman_df["Select Bibliography"].notna()]
roman_sources = filtered_df["Select Bibliography"]

sources = set()
index = 0
for values in roman_sources:
    values = values.replace(".", "").split(";")
    sources |= set([x.strip() for x in values if x.strip() != ""])

print(len(sources))