import geopandas as gpd

gdf = gpd.read_file(
    "data/processed/enriched/facilities_land.geojson"
)

print(gdf.info())

print()

print(f"Total Facilities : {len(gdf)}")

print()

print("Missing Land Values:")
print(gdf["land_value_eur_m2"].isna().sum())

print()

print("First 10 Records")

print(
    gdf[
        [
            "company",
            "name",
            "municipality",
            "district",
            "land_value_eur_m2",
        ]
    ].head(10)
)