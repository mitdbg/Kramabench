import geopandas as gpd
data_path = "./data/wildfire/input/"

gdf_usa = gpd.read_file(f"{data_path}/usa.gpkg")
gdf_nifc = gpd.read_file(f"{data_path}/nifc_geographic_areas.gpkg")

# Ensure same CRS
gdf_nifc = gdf_nifc.to_crs(gdf_usa.crs)

# Dissolve state geometries
gdf_usa_dissolved = gdf_usa.dissolve(by='adm1_name', as_index=False)

# Perform spatial join
joined = gpd.sjoin(gdf_usa_dissolved, gdf_nifc, how='right', predicate='intersects')

# Group by NIFC region and aggregate both count and list of states
result = (joined.groupby(['GACCName', 'GACCAbbreviation'])
          .agg({
              'adm1_name': [('Number_of_States', 'nunique'),
                           ('States', lambda x: list(set(x)))]
          })
          .reset_index())

# Flatten column names
result.columns = ['GACC_Name', 'GACC_Abbreviation', 'Number_of_States', 'States']

# Sort by number of states (descending)
result = result.sort_values('Number_of_States', ascending=False)

# Get the region(s) with the maximum number of states
max_states = result['Number_of_States'].max()
top_regions = result[result['Number_of_States'] == max_states]

print("\nNIFC Geographic Area(s) intersecting with the most states:")
for _, row in top_regions.iterrows():
    print(f"\nGACC Name: {row['GACC_Name']}")
    print(f"GACC Abbreviation: {row['GACC_Abbreviation']}")
    print(f"Number of intersecting states: {row['Number_of_States']}")
    print("States:", ", ".join(sorted(row['States'])))