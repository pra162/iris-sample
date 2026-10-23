import geopandas as gpd


class PowerScore:
    """
    Power Intelligence Scoring

    This module calculates a Power Readiness Score for each data center
    based on proximity to:

    - Substations
    - Power Lines
    - Transformers

    Outputs:
    - substation_score
    - power_line_score
    - transformer_score
    - power_readiness_score
    - power_rating
    - power_rank
    """

    def __init__(self, facilities: gpd.GeoDataFrame):
        self.facilities = facilities

    def calculate(self) -> gpd.GeoDataFrame:

        print("--------------------------------")
        print("Calculating Power Readiness Score...")

        # ------------------------------------------------------------
        # Calculate individual scores
        # ------------------------------------------------------------

        self.facilities["substation_score"] = self.facilities[
            "distance_to_substation_m"
        ].apply(self._distance_score)

        self.facilities["power_line_score"] = self.facilities[
            "distance_to_power_line_m"
        ].apply(self._distance_score)

        self.facilities["transformer_score"] = self.facilities[
            "distance_to_transformer_m"
        ].apply(self._distance_score)

        # ------------------------------------------------------------
        # Calculate weighted score
        # ------------------------------------------------------------

        self.facilities["power_readiness_score"] = (
            self.facilities["substation_score"] * 0.40
            + self.facilities["power_line_score"] * 0.35
            + self.facilities["transformer_score"] * 0.25
        ).round(2)

        # ------------------------------------------------------------
        # Rating
        # ------------------------------------------------------------

        self.facilities["power_rating"] = self.facilities[
            "power_readiness_score"
        ].apply(self._rating)

        # ------------------------------------------------------------
        # Ranking
        # ------------------------------------------------------------

        self.facilities["power_rank"] = (
            self.facilities["power_readiness_score"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )

        print("Power Readiness Score calculated.")

        # ------------------------------------------------------------
        # Determine which columns to display
        # ------------------------------------------------------------

        display_columns = []

        for column in [
            "company",
            "name",
            "facility_name",
            "site_name",
            "title",
        ]:
            if column in self.facilities.columns:
                display_columns.append(column)

        display_columns.extend([
            "power_readiness_score",
            "power_rating",
            "power_rank",
        ])

        print("\nTop 10 Power Scores\n")

        print(
            self.facilities[display_columns]
            .sort_values(
                by="power_readiness_score",
                ascending=False
            )
            .head(10)
            .to_string(index=False)
        )

        return self.facilities

    @staticmethod
    def _distance_score(distance: float) -> int:
        """
        Distance Scoring

        <= 100 m   -> 100
        <= 250 m   -> 90
        <= 500 m   -> 80
        <= 1000 m  -> 60
        > 1000 m   -> 40
        """

        if distance <= 100:
            return 100

        if distance <= 250:
            return 90

        if distance <= 500:
            return 80

        if distance <= 1000:
            return 60

        return 40

    @staticmethod
    def _rating(score: float) -> str:
        """
        Distance Scoring

        <= 100 m   -> 100
        <= 250 m   -> 90
        <= 500 m   -> 80
        <= 1000 m  -> 60
        > 1000 m   -> 40
        """

        if score >= 90:
            return "Excellent"

        if score >= 75:
            return "Very Good"

        if score >= 60:
            return "Good"

        if score >= 40:
            return "Fair"

        return "Poor"