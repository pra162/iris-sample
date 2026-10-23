import geopandas as gpd

gdf = gpd.read_file("data/raw/boris/BRW_2026.shp")

print(gdf.crs)
print()
print(gdf.columns)
print()
print(gdf.head())
print("\n===== BRW Statistics =====")
print(gdf["BRW"].describe())

print("\n===== First 20 BRW Values =====")
print(gdf["BRW"].head(20))

print("\n===== Municipality Columns =====")
print(gdf[["GEMA", "GENA", "ORTST", "PLZ"]].head(20))