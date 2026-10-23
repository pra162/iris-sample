from __future__ import annotations

from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from geoalchemy2 import Geography

from app.database.models.facility import Facility
from app.database.repositories.base_repository import BaseRepository


class FacilityRepository(
    BaseRepository[Facility]
):
    """
    Repository responsible for Facility-specific
    database operations.
    """

    def __init__(
        self,
        session: Session,
    ):

        super().__init__(
            session,
            Facility,
        )

    # ======================================================
    # SOURCE ID
    # ======================================================

    def find_by_source_id(
        self,
        source_id: int,
    ) -> Facility | None:

        statement = (
            select(Facility)
            .where(
                Facility.source_id == source_id
            )
            .limit(1)
        )

        return self.session.scalar(
            statement
        )

    # ======================================================
    # COMPANY
    # ======================================================

    def find_by_company(
        self,
        company: str,
    ) -> list[Facility]:

        statement = (
            select(Facility)
            .where(
                Facility.company == company
            )
            .order_by(
                Facility.name
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # CITY
    # ======================================================

    def find_by_city(
        self,
        city: str,
    ) -> list[Facility]:

        statement = (
            select(Facility)
            .where(
                Facility.city == city
            )
            .order_by(
                Facility.name
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # COUNTRY
    # ======================================================

    def find_by_country(
        self,
        country: str,
    ) -> list[Facility]:

        statement = (
            select(Facility)
            .where(
                Facility.country == country
            )
            .order_by(
                Facility.name
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # NAME
    # ======================================================

    def find_by_name(
        self,
        name: str,
    ) -> Facility | None:

        statement = (
            select(Facility)
            .where(
                Facility.name == name
            )
            .limit(1)
        )

        return self.session.scalar(
            statement
        )

    # ======================================================
    # SEARCH
    # ======================================================

    def search(
        self,
        keyword: str,
    ) -> list[Facility]:

        keyword = f"%{keyword}%"

        statement = (
            select(Facility)
            .where(
                Facility.name.ilike(keyword)
                | Facility.company.ilike(keyword)
                | Facility.city.ilike(keyword)
            )
            .order_by(
                Facility.company,
                Facility.name,
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # STATISTICS
    # ======================================================

    def count_by_country(
        self,
        country: str,
    ) -> int:

        statement = (
            select(func.count())
            .select_from(Facility)
            .where(
                Facility.country == country
            )
        )

        return (
            self.session.scalar(
                statement
            )
            or 0
        )

    def count_by_company(
        self,
        company: str,
    ) -> int:

        statement = (
            select(func.count())
            .select_from(Facility)
            .where(
                Facility.company == company
            )
        )

        return (
            self.session.scalar(
                statement
            )
            or 0
        )

    # ======================================================
    # ID
    # ======================================================

    def find_by_id(
        self,
        facility_id: str,
    ) -> Facility | None:

        return self.session.get(
            Facility,
            facility_id,
        )

    # ======================================================
    # NEAREST FACILITY
    # ======================================================

    def find_nearest_facility(
        self,
        latitude: float,
        longitude: float,
    ) -> Facility | None:

        point = func.ST_SetSRID(
            func.ST_Point(
                longitude,
                latitude,
            ),
            4326,
        )

        statement = (
            select(Facility)
            .where(
                Facility.geometry.is_not(None)
            )
            .order_by(
                func.ST_Distance(
                    cast(
                        Facility.geometry,
                        Geography,
                    ),
                    cast(
                        point,
                        Geography,
                    ),
                )
            )
            .limit(1)
        )

        return self.session.scalar(
            statement
        )

    # ======================================================
    # CITIES
    # ======================================================

    def get_all_cities(
        self,
    ) -> list[str]:

        statement = (
            select(Facility.city)
            .where(
                Facility.city.is_not(None)
            )
            .distinct()
            .order_by(
                Facility.city
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # COMPANIES
    # ======================================================

    def get_all_companies(
        self,
    ) -> list[str]:

        statement = (
            select(Facility.company)
            .where(
                Facility.company.is_not(None)
            )
            .distinct()
            .order_by(
                Facility.company
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # NEARBY SEARCH
    # ======================================================

    def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25,
    ) -> list[Facility]:

        point = func.ST_SetSRID(
            func.ST_Point(
                longitude,
                latitude,
            ),
            4326,
        )

        radius_meters = radius_km * 1000

        statement = (
            select(Facility)
            .where(
                Facility.geometry.is_not(None)
            )
            .where(
                func.ST_DWithin(
                    cast(
                        Facility.geometry,
                        Geography,
                    ),
                    cast(
                        point,
                        Geography,
                    ),
                    radius_meters,
                )
            )
            .order_by(
                func.ST_Distance(
                    cast(
                        Facility.geometry,
                        Geography,
                    ),
                    cast(
                        point,
                        Geography,
                    ),
                )
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ======================================================
    # FACILITY NAMES
    # ======================================================

    def get_all_facility_names(
        self,
    ) -> list[str]:

        rows = (
            self.session.query(
                Facility.name,
            )
            .order_by(
                Facility.name,
            )
            .all()
        )

        return [
            row[0]
            for row in rows
            if row[0]
        ]