from enum import Enum

from sqlalchemy.orm import Session

from app.database.repositories.facility_repository import (
    FacilityRepository,
)

from app.services.site_intelligence_service import (
    SiteIntelligenceService,
)


class RankingType(str, Enum):
    OVERALL = "overall"
    GRID = "grid"
    TRANSMISSION = "transmission"
    TRANSFORMER = "transformer"
    RENEWABLE = "renewable"
    LAND = "land"
    EXPANSION = "expansion"


class SiteRankingService:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

        self.facility_repository = FacilityRepository(
            session
        )
        self.site_service = SiteIntelligenceService(
            session
        )

    # ======================================================
    # Public
    # ======================================================

    def rank_sites(
        self,
        ranking_type: RankingType = RankingType.OVERALL,
        limit: int = 10,
    ) -> list[dict]:
        """
        Returns ranked facilities using the
        Site Intelligence engine.
        """

        facilities = (
            self.facility_repository.get_all()
        )

        results = []

        score_field = self._score_field(ranking_type)

        for facility in facilities:

            try:
                intelligence = self.site_service.analyze_facility(
                    facility.id
                )

                if intelligence is None:
                    continue

                score = intelligence["site_score"]

                results.append(
                    {
                        "facility_id": facility.id,
                        "company": facility.company,
                        "facility": facility.name,
                        "city": facility.city,
                        "country": facility.country,

                        "overall_score": score["overall_score"],
                        "grid_score": score["grid_score"],
                        "transmission_score": score["transmission_score"],
                        "transformer_score": score["transformer_score"],
                        "renewable_score": score["renewable_score"],
                        "land_score": score["land_score"],
                        "expansion_score": score["expansion_score"],

                        "ranking_score": score[score_field],
                    }
                )

            except Exception:
                import traceback

                print("=" * 80)
                print(f"Facility: {facility.company} | {facility.name}")
                traceback.print_exc()
                print("=" * 80)

                continue

        results.sort(
            key=lambda row: row["ranking_score"],
            reverse=True,
        )

        for index, row in enumerate(results):
            row["rank"] = index + 1

        return results[:limit]

    # ======================================================
    # Private
    # ======================================================

    def _score_field(
        self,
        ranking_type: RankingType,
    ) -> str:

        mapping = {

            RankingType.OVERALL:
                "overall_score",

            RankingType.GRID:
                "grid_score",

            RankingType.TRANSMISSION:
                "transmission_score",

            RankingType.TRANSFORMER:
                "transformer_score",

            RankingType.RENEWABLE:
                "renewable_score",

            RankingType.LAND:
                "land_score",

            RankingType.EXPANSION:
                "expansion_score",
        }

        return mapping[ranking_type]