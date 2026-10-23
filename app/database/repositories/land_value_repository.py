from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.land_value import LandValue
from app.database.repositories.base_repository import BaseRepository
import math

class LandValueRepository(BaseRepository[LandValue]):
    """
    Repository for BORIS NRW land values.
    """

    def __init__(self, session: Session):
        super().__init__(session, LandValue)

    def find_by_id(
        self,
        land_value_id: int,
    ) -> LandValue | None:

        return self.session.get(
            LandValue,
            land_value_id,
        )

    def find_by_postal_code(
        self,
        postal_code: str,
    ) -> list[LandValue]:

        statement = (
            select(LandValue)
            .where(
                LandValue.postal_code == postal_code
            )
            .order_by(
                LandValue.municipality
            )
        )

        return list(
            self.session.scalars(statement)
        )

    def find_by_municipality(
        self,
        municipality: str,
    ) -> list[LandValue]:

        statement = (
            select(LandValue)
            .where(
                LandValue.municipality == municipality
            )
            .order_by(
                LandValue.postal_code
            )
        )

        return list(
            self.session.scalars(statement)
        )

    def count(self) -> int:

        statement = (
            select(func.count())
            .select_from(LandValue)
        )

        return self.session.scalar(statement)

    def delete_all(self) -> None:

        self.session.query(
            LandValue
        ).delete()

        self.session.commit()
    
    def find_nearest_land_value(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Returns the nearest valid BORIS land value.
        """

        point = func.ST_Transform(
            func.ST_SetSRID(
                func.ST_Point(
                    longitude,
                    latitude,
                ),
                4326,
            ),
            25832,
        )

        distance = (
            func.ST_Distance(
                LandValue.geometry,
                point,
            )
            / 1000
        ).label("distance_km")

        statement = (
            select(
                LandValue.id,
                LandValue.municipality,
                LandValue.district,
                LandValue.postal_code,
                LandValue.land_value_eur_m2,
                distance,
            )
            .where(
                LandValue.land_value_eur_m2.is_not(None),
            )
            .order_by(distance)
            .limit(1)
        )

        result = self.session.execute(statement).first()

        if result is None:
            return None

        value = result.land_value_eur_m2

        if value is None:
            return None

        if math.isnan(value):
            return None

        return {
            "id": result.id,
            "municipality": result.municipality,
            "district": result.district,
            "postal_code": result.postal_code,
            "land_value_eur_m2": (
                round(result.land_value_eur_m2, 2)
                if result.land_value_eur_m2 is not None
                else None
            ),
            "distance_km": (
                round(result.distance_km, 2)
                if result.distance_km is not None
                else None
            ),
        }