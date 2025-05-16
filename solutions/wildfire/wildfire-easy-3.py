import pandas as pd
import numpy as np
import geopandas as gpd
data_path = "./data/wildfire/input/"
gdf_usa = gpd.read_file(f"{data_path}/usa.gpkg")
gdf_nifc = gpd.read_file(f"{data_path}/nifc_geographic_areas.gpkg")

# 1. Ensure both GeoDataFrames have the same CRS (Coordinate Reference System)
gdf_nifc = gdf_nifc.to_crs(gdf_usa.crs)

# 2. Dissolve the state geometries to ensure each state is represented by a single geometry
gdf_usa_dissolved = gdf_usa.dissolve(by='adm1_name', as_index=False)

# 3. Perform a spatial join
joined = gpd.sjoin(gdf_usa_dissolved, gdf_nifc, how='left', predicate='intersects')

# Group by state and aggregate both count and list of NIFC regions
result = (joined.groupby('adm1_name')
          .agg({
              'GACCAbbreviation': [('Number_of_NIFC_Regions', 'nunique'),
                          ('NIFC_Regions', lambda x: list(set(x)))]
          })
          .reset_index())

# Flatten column names
result.columns = ['State', 'Number_of_NIFC_Regions', 'NIFC_Regions']

# Sort by number of regions (descending)
result = result.sort_values('Number_of_NIFC_Regions', ascending=False)

# Display the result
print(result)