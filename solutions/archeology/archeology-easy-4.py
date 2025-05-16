#!/usr/bin/env python
# coding: utf-8


import pandas as pd
data_path = "./data/archeology/input/"


climateMeasurementsPath = data_path + "climateMeasurements.xlsx"
climateXlsx = pd.ExcelFile(climateMeasurementsPath)
sheet_name = climateXlsx.sheet_names[0]
climateDF = pd.read_excel(climateXlsx, sheet_name=sheet_name, header=0, skiprows=5)



climateDF.keys()



climateDF = climateDF.dropna(axis=1, how='all')
climateDF["year"] = 1950 - climateDF["Age_ky.1"].round(0) * 1000



minDust = climateDF["ODP 967 Dust proxy"].min()
minDustValues = climateDF[climateDF["ODP 967 Dust proxy"] == minDust]
minDustRow = minDustValues[minDustValues["ODP 967 wet-dry index"] == minDustValues["ODP 967 wet-dry index"].min()]
print(minDustRow)


print(minDustRow["Ca"].values[0])




