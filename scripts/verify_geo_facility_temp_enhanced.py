import geopandas as gpd

gdf = gpd.read_file(
    "data/processed/datacentermap/facilities.geojson"
)

print(gdf.is_valid.value_counts())

print()

print(gdf.geometry.is_empty.value_counts())

print()

print(gdf[gdf.geometry.is_empty])

print()

print(gdf[gdf.geometry.isna()])