import geopandas as gpd


class NearestSpatial:

    @staticmethod
    def find_nearest(
        source_gdf: gpd.GeoDataFrame,
        target_gdf: gpd.GeoDataFrame,
        target_type: str,
        name_column: str = "name"
    ) -> gpd.GeoDataFrame:

        print("--------------------------------")
        print(f"Finding nearest {target_type}...")

        if source_gdf.empty:
            raise ValueError("Source GeoDataFrame is empty.")

        if target_gdf.empty:
            raise ValueError("Target GeoDataFrame is empty.")

        if source_gdf.crs != target_gdf.crs:
            raise ValueError("Both GeoDataFrames must use the same CRS.")

        # -------------------------------------------------------
        # Rename BEFORE joining to avoid name_left/name_right
        # -------------------------------------------------------

        if name_column not in target_gdf.columns:
            raise ValueError(
                f"Column '{name_column}' not found in target GeoDataFrame."
            )

        target = target_gdf[[name_column, "geometry"]].copy()

        target.rename(
            columns={
                name_column: f"nearest_{target_type}"
            },
            inplace=True
        )

        result = gpd.sjoin_nearest(
            source_gdf,
            target,
            how="left",
            distance_col=f"distance_to_{target_type}_m"
        )

        # -------------------------------------------------------
        # Remove duplicate nearest matches
        # -------------------------------------------------------

        result = result.loc[
            ~result.index.duplicated(keep="first")
        ].copy()

        # Remove GeoPandas helper column
        if "index_right" in result.columns:
            result.drop(
                columns=["index_right"],
                inplace=True
            )

        print(
            f"Nearest {target_type} calculated for "
            f"{len(result)} facilities."
        )

        return result