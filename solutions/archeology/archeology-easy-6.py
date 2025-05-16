#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
data_path = "./data/archeology/input/"



citiesPath = data_path + "worldcities.csv"
cities = pd.read_csv(citiesPath)


citiesInWest = cities[cities["lng"] < 0]
citiesInSouth = citiesInWest[citiesInWest["lat"] < 0]
highestCity = citiesInSouth[citiesInSouth["population"] == citiesInSouth["population"].max()]
print(highestCity["city"].values[0])

