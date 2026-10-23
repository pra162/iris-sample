import geopandas as gpd

gdf = gpd.read_file(
    "data/processed/datacentermap/facilities.geojson"
)

print(gdf.info())
print()
print(gdf.head())
print()
print(gdf.geometry.geom_type.value_counts())