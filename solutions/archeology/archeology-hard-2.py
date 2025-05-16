#!/usr/bin/env python
# coding: utf-8

import pandas as pd
data_path = "../../input/"


radioCarbonPath = data_path + "radiocarbon_database_regional.xlsx"
climateMeasurementsPath = data_path + "climateMeasurements.xlsx"

# Read the Excels
carbonXlsx = pd.ExcelFile(radioCarbonPath)
climateXlsx = pd.ExcelFile(climateMeasurementsPath)

# Get the first sheet name
sheet_name = carbonXlsx.sheet_names[0]
radioCarbonDF = pd.read_excel(carbonXlsx, sheet_name=sheet_name)

sheet_name = climateXlsx.sheet_names[0]
climateDF = pd.read_excel(climateXlsx, sheet_name=sheet_name, header=0, skiprows=5)



#drop all rows with all NaN values
radioCarbonDF = radioCarbonDF.dropna(how='all')
#drop all columns with all NaN values
radioCarbonDF = radioCarbonDF.dropna(axis=1, how='all')
radioCarbonDF["year"] = 1950 - radioCarbonDF["date"]
#drop all rows with all NaN values
climateDF = climateDF.dropna(how='all')
#drop all columns with all NaN values
climateDF = climateDF.dropna(axis=1, how='all')
climateDF["year"] = 1950 - climateDF["Age_ky.1"].round(0) * 1000


def is_increasing(row):
    year = row["year"]
    differences = climateDF["year"] - year
    
    previous_year = climateDF[climateDF["year"] < year].sort_values("year", ascending=False).head(1)
    next_year = climateDF[climateDF["year"] > year].sort_values("year", ascending=True).head(1)

    try:
        previous_year = previous_year.iloc[0]
        last_wet = previous_year['ODP 967 wet-dry index']
    except IndexError:
        last_wet = 0

    try:
        next_year = next_year.iloc[0]
        next_wet = next_year['ODP 967 wet-dry index']
    except IndexError:
        next_wet = last_wet

    differences = next_wet - last_wet
    if differences > 0:
        return 1
    else:
        return 0


climateDF["isIncreasing"] = climateDF.apply(is_increasing, axis=1)
print("Percent of increasing values: ", round(climateDF["isIncreasing"].mean(), 4))