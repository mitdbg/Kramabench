#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
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



radioCarbonDF.keys()
homoSapiens = radioCarbonDF[radioCarbonDF["Species"] == "Homo sapiens"]
print("Number of human samples: ", len(homoSapiens))


homoSapiens["year"] = 1950 - radioCarbonDF["date"]
neolithic = homoSapiens[homoSapiens["Culture"] == "Neolithic"]

print("Number of Neolithic samples: ", len(neolithic))


mostNorthernNeolithic = neolithic[neolithic["Latitude"] == neolithic["Latitude"].max()]



print("Most Northern Neolithic Sample: ", mostNorthernNeolithic["Latitude"].values[0])



mostNorthernNeolithic = mostNorthernNeolithic[mostNorthernNeolithic["year"] == mostNorthernNeolithic["year"].max()]
mostNorthernYear = mostNorthernNeolithic["year"].values[0]


print("Most northern Neolithic sample year: ", mostNorthernYear)


#drop all rows with all NaN values
climateDF = climateDF.dropna(how='all')
#drop all columns with all NaN values
climateDF = climateDF.dropna(axis=1, how='all')
climateDF["year"] = 1950 - climateDF["Age_ky.1"].round(0) * 1000


def find_closest(targetValue, possibleValues):
    return possibleValues.iloc[(np.abs(possibleValues - targetValue)).argmin()]


closestYear = find_closest(mostNorthernYear, climateDF["year"])
closestYearValues = climateDF[climateDF["year"] == closestYear]
print(climateDF[climateDF["year"] == closestYear])
print(len(closestYearValues))



print(round(closestYearValues["Al"].max(), 4))

