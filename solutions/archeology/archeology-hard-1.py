#!/usr/bin/env python
# coding: utf-8

import pandas as pd

data_path = "./data/archeology/input/"


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



round(climateDF["year"].mean(), 4)



def find_closest_year(row):
    year = row["year"]
    differences = climateDF["year"] - year
    
    previous_year = climateDF[climateDF["year"] <= year].sort_values("year", ascending=False).head(1)
    next_year = climateDF[climateDF["year"] >= year].sort_values("year", ascending=True).head(1)

    previous_year = previous_year.iloc[0]
    next_year = next_year.iloc[0]

    if previous_year["year"] == year:
        return previous_year["K"]
    if next_year["year"] == year:
        return next_year["K"]

    last_K = previous_year["K"]
    next_K = next_year["K"]

    interpolation = (year - previous_year["year"]) / (next_year["year"] - previous_year["year"])
    K = last_K + interpolation * (next_K - last_K)
    return K



maltaDF = radioCarbonDF[radioCarbonDF["Region"] == "Malta"]
humansExistedInArea = (maltaDF["year"].min(), maltaDF["year"].max())
KValuesForHumans = []
for i in range(humansExistedInArea[0], humansExistedInArea[1]):
    KValue = find_closest_year({"year": i})
    KValuesForHumans.append(KValue)

print("Mean K value for humans in the area: ", round(sum(KValuesForHumans) / len(KValuesForHumans), 4))




