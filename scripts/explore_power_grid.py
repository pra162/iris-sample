import geopandas as gpd

gdf = gpd.read_file("data/processed/overpass/power_grid.geojson")

print(gdf.info())
print()

print(gdf.geometry.geom_type.value_counts())
print()

print(gdf["power_type"].value_counts())
print()

print(gdf.head())