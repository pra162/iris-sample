"""
Site Score Service

Responsible for calculating the overall
Data Center Site Intelligence Score.

The score is composed of multiple weighted
infrastructure categories.

Maximum Score: 100
"""

from dataclasses import dataclass, asdict

# ==========================================================
# Weights
# ==========================================================

GRID_WEIGHT = 25
TRANSMISSION_WEIGHT = 20
TRANSFORMER_WEIGHT = 15
RENEWABLE_WEIGHT = 10
LAND_WEIGHT = 15
EXPANSION_WEIGHT = 15


# ==========================================================
# Result Model
# ==========================================================

@dataclass
class SiteScoreResult:

    overall_score: int
    rating: str

    grid_score: int
    transmission_score: int
    transformer_score: int
    renewable_score: int
    land_score: int
    expansion_score: int

    def to_dict(self):
        return asdict(self)


# ==========================================================
# Service
# ==========================================================

class SiteScoreService:
    """
    Calculates the overall infrastructure
    suitability score.
    """

    @classmethod
    def calculate(
        cls,
        site: dict,
    ) -> SiteScoreResult:

        grid = cls._grid_score(site)

        transmission = cls._transmission_score(site)

        transformer = cls._transformer_score(site)

        renewable = cls._renewable_score(site)

        land = cls._land_score(site)

        expansion = cls._expansion_score(site)

        overall = min(
            100,
            grid
            + transmission
            + transformer
            + renewable
            + land
            + expansion,
        )

        return SiteScoreResult(
            overall_score=overall,

            rating=cls._rating(overall),

            grid_score=grid,

            transmission_score=transmission,

            transformer_score=transformer,

            renewable_score=renewable,

            land_score=land,

            expansion_score=expansion,
        )

    # ======================================================
    # Individual Scores
    # ======================================================

    @staticmethod
    def _grid_score(site: dict) -> int:

        substation = site["power"]["nearest_substation"]

        if not substation:
            return 0

        distance = substation["distance_km"]

        if distance <= 0.5:
            return 25

        if distance <= 1:
            return 22

        if distance <= 2:
            return 18

        if distance <= 5:
            return 12

        return 5

    @staticmethod
    def _transmission_score(site: dict) -> int:

        line = site["power"]["nearest_high_voltage_line"]

        if not line:
            return 0

        distance = line["distance_km"]
        voltage = line["voltage"] or ""

        if distance <= 0.5:
            score = 12
        elif distance <= 1:
            score = 10
        elif distance <= 2:
            score = 8
        elif distance <= 5:
            score = 5
        else:
            score = 2

        if "380000" in voltage:
            score += 8
        elif "220000" in voltage:
            score += 6
        elif "110000" in voltage:
            score += 4

        return min(score, 20)

    @staticmethod
    def _transformer_score(site: dict) -> int:

        transformer = site["power"]["nearest_transformer"]

        if not transformer:
            return 0

        distance = transformer["distance_km"]

        if distance <= 0.5:
            return 15

        if distance <= 1:
            return 13

        if distance <= 2:
            return 10

        if distance <= 5:
            return 6

        return 2

    @staticmethod
    def _renewable_score(site: dict) -> int:

        energy = site["renewable_energy"]

        assets = energy["asset_count"]
        capacity = energy["solar_kw"] + energy["wind_kw"]

        score = 0

        if assets >= 10:
            score += 5
        elif assets >= 5:
            score += 3
        elif assets >= 1:
            score += 1

        if capacity >= 10000:
            score += 5
        elif capacity >= 5000:
            score += 3
        elif capacity >= 1000:
            score += 1

        return min(score, 10)
    @staticmethod
    def _land_score(site: dict) -> int:

        value = site["land"]["land_value_eur_m2"]

        if value is None:
            return 0

        if value <= 100:
            return 15

        if value <= 250:
            return 12

        if value <= 500:
            return 9

        if value <= 1000:
            return 6

        return 3

    @staticmethod
    def _expansion_score(site: dict) -> int:
        """
        Placeholder.

        Future:
        - Zoning
        - Available land
        - Environmental constraints
        """

        return EXPANSION_WEIGHT

    # ======================================================
    # Rating
    # ======================================================

    @staticmethod
    def _rating(score: int) -> str:

        if score >= 90:
            return "Excellent"

        if score >= 75:
            return "Very Good"

        if score >= 60:
            return "Good"

        if score >= 45:
            return "Moderate"

        return "Poor"