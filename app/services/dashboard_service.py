from __future__ import annotations

from math import isnan
from dataclasses import asdict

from sqlalchemy.orm import Session

from app.database.repositories.energy_asset_repository import (
    EnergyAssetRepository,
)
from app.database.repositories.facility_repository import (
    FacilityRepository,
)
from app.database.repositories.land_value_repository import (
    LandValueRepository,
)
from app.database.repositories.power_infrastructure_repository import (
    PowerInfrastructureRepository,
)

from app.services.site_intelligence_service import (
    SiteIntelligenceService,
)

from app.services.site_ranking_service import (
    SiteRankingService,
    RankingType,
)

from app.services.news_intelligence_service import (
    NewsIntelligenceService,
)


class DashboardService:
    """
    Service responsible for aggregating dashboard data from
    multiple repositories.

    The Streamlit UI should communicate only with this service
    instead of directly accessing repositories.
    """

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

        # -------------------------------------------------
        # Repositories
        # -------------------------------------------------

        self.facility_repository = (
            FacilityRepository(session)
        )

        self.energy_repository = (
            EnergyAssetRepository(session)
        )

        self.land_repository = (
            LandValueRepository(session)
        )

        self.power_repository = (
            PowerInfrastructureRepository(session)
        )

        # -------------------------------------------------
        # Services
        # -------------------------------------------------

        self.site_service = (
            SiteIntelligenceService(session)
        )

        self.news_service = (
            NewsIntelligenceService(session)
        )

    # ======================================================
    # Dashboard Summary
    # ======================================================

    def get_dashboard_summary(
        self,
    ) -> dict:
        """
        Return the main KPI summary for the dashboard.
        """

        average_land_value = (
            self.get_average_land_value()
        )

        if (
            isinstance(
                average_land_value,
                float,
            )
            and isnan(
                average_land_value,
            )
        ):
            average_land_value = 0.0

        return {
            # -------------------------------------------------
            # Main KPIs
            # -------------------------------------------------

            "facilities": (
                self.get_facility_count()
            ),

            "energy_assets": (
                self.get_energy_asset_count()
            ),

            "power_infrastructure": (
                self.get_power_infrastructure_count()
            ),

            "average_land_value": (
                average_land_value
            ),

            "average_site_score": (
                self.get_average_site_score()
            ),

            "news_signals": (
                self.get_news_signal_count()
            ),

            # -------------------------------------------------
            # Temporary trend values
            #
            # These will later be calculated from
            # historical pipeline runs.
            # -------------------------------------------------

            "facilities_trend": 0,

            "power_trend": 0,

            "energy_trend": 0,

            "land_trend": 0,

            "news_trend": 0,

            "site_score_trend": 0,
        }

    # ======================================================
    # Facilities
    # ======================================================

    def get_facility_count(
        self,
    ) -> int:
        """
        Return the total number of facilities.
        """

        return (
            self.facility_repository.count()
        )

    # ======================================================
    # Energy Assets
    # ======================================================

    def get_energy_asset_count(
        self,
    ) -> int:
        """
        Return the total number of energy assets.
        """

        return (
            self.energy_repository.count()
        )

    # ======================================================
    # Power Infrastructure
    # ======================================================

    def get_power_infrastructure_count(
        self,
    ) -> int:
        """
        Return the total number of power
        infrastructure assets.
        """

        return (
            self.power_repository.count()
        )

    # ======================================================
    # Land Values
    # ======================================================

    def get_average_land_value(
        self,
    ) -> float:
        """
        Calculate the average land value
        across available land-value records.
        """

        land_values = (
            self.land_repository.get_all()
        )

        if not land_values:
            return 0.0

        values = []

        for entity in land_values:

            value = (
                entity.land_value_eur_m2
            )

            if value is None:
                continue

            if (
                isinstance(
                    value,
                    float,
                )
                and isnan(value)
            ):
                continue

            values.append(value)

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            2,
        )

    # ======================================================
    # Site Score
    # ======================================================

    def get_average_site_score(
        self,
    ) -> int:
        """
        Return the average site score.

        Temporary implementation.

        The actual Site Scoring Engine will be
        connected here once its database integration
        is verified.
        """

        return 82

    # ======================================================
    # News
    # ======================================================

    def get_news_signal_count(
        self,
    ) -> int:
        """
        Return the number of news intelligence
        matches stored in PostgreSQL.

        News data is accessed through the
        NewsIntelligenceService.
        """

        return (
            self.news_service.get_signal_count()
        )

    # ======================================================
    # Facilities Map
    # ======================================================

    def get_facilities_for_map(
        self,
    ) -> list[dict]:
        """
        Return facilities with valid coordinates
        for the dashboard map.
        """

        facilities = (
            self.facility_repository.get_all()
        )

        result = []

        for facility in facilities:

            if (
                facility.latitude is None
                or facility.longitude is None
            ):
                continue

            result.append(
                {
                    "id": facility.id,

                    "company": (
                        facility.company
                    ),

                    "name": (
                        facility.name
                    ),

                    "city": (
                        facility.city
                    ),

                    "country": (
                        facility.country
                    ),

                    "latitude": (
                        facility.latitude
                    ),

                    "longitude": (
                        facility.longitude
                    ),
                }
            )

        return result

    # ======================================================
    # Energy Assets Map
    # ======================================================

    def get_energy_assets_for_map(
        self,
    ) -> list[dict]:
        """
        Return renewable energy assets as plain
        dictionaries for the dashboard map.
        """

        energy_assets = (
            self.energy_repository.get_all()
        )

        result = []

        for asset in energy_assets:

            if (
                asset.latitude is None
                or asset.longitude is None
            ):
                continue

            result.append(
                {
                    "id": asset.id,

                    "name": (
                        asset.name
                    ),

                    "energy_type": (
                        asset.energy_type
                    ),

                    "operator": (
                        asset.operator_name
                    ),

                    "status": (
                        asset.status
                    ),

                    "gross_power_kw": (
                        asset.gross_power_kw
                    ),

                    "latitude": (
                        asset.latitude
                    ),

                    "longitude": (
                        asset.longitude
                    ),
                }
            )

        return result

    # ======================================================
    # High Voltage Substations
    # ======================================================

    def get_high_voltage_substations_for_map(
        self,
    ) -> list[dict]:
        """
        Return strategic high-voltage substations
        for the dashboard map.
        """

        substations = (
            self.power_repository
            .get_high_voltage_substations()
        )

        return [
            dict(substation)
            for substation in substations
        ]

    # ======================================================
    # High Voltage Lines
    # ======================================================

    def get_high_voltage_lines_for_map(
        self,
    ) -> list[dict]:
        """
        Return high-voltage transmission lines
        for the dashboard map.
        """

        lines = (
            self.power_repository
            .get_high_voltage_lines()
        )

        return [
            dict(line)
            for line in lines
        ]

    # ======================================================
    # Strategic Transformers
    # ======================================================

    def get_transformers_for_map(
        self,
    ) -> list[dict]:
        """
        Return strategic transformers
        for the dashboard map.
        """

        transformers = (
            self.power_repository
            .get_strategic_transformers()
        )

        return [
            dict(transformer)
            for transformer in transformers
        ]

    # ======================================================
    # Site Intelligence
    # ======================================================

    def get_site_intelligence(
        self,
        facility_id: int,
    ):
        """
        Return complete Site Intelligence
        for a facility.
        """

        return (
            self.site_service.analyze_facility(
                facility_id
            )
        )

    # ======================================================
    # Location Analysis
    # ======================================================

    def analyze_location(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Analyze an arbitrary map location.
        """

        return (
            self.site_service.analyze_location(
                latitude,
                longitude,
            )
        )

    # ======================================================
    # Facility From Map Click
    # ======================================================

    def get_facility_from_click(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Find the nearest facility to a map click.
        """

        return (
            self.facility_repository
            .find_nearest_facility(
                latitude,
                longitude,
            )
        )

    # ======================================================
    # Site Ranking
    # ======================================================

    def get_top_ranked_sites(
        self,
        limit: int = 5,
    ):
        """
        Return the top-ranked sites.
        """

        return (
            SiteRankingService(
                self.session,
            ).rank_sites(
                ranking_type=RankingType.OVERALL,
                limit=limit,
            )
        )

    # ======================================================
    # Latest News
    # ======================================================

    def get_latest_news(
        self,
        limit: int = 5,
    ):
        """
        Return the latest news intelligence.
        """

        return (
            self.news_service.latest_news(
                limit,
            )
        )