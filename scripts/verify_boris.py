import geopandas as gpd

gdf = gpd.read_file(
    "data/processed/boris/land_values.geojson"
)

print(gdf.info())

print()

print(gdf.head())

print()

print(gdf.crs)

print()

print(gdf["land_value_eur_m2"].describe())