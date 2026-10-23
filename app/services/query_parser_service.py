"""
Query Parser Service

Parses natural language questions into
structured business queries.

This service NEVER calls OpenAI.

Responsibilities
- Normalize questions
- Detect entities
- Extract search parameters
- Return structured query

Author:
NRW BI Platform
"""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.database.repositories.facility_repository import (
    FacilityRepository,
)



class QueryParserService:
    """
    Parses user questions into structured data.

    The parser is responsible for extracting
    entities such as cities, companies, limits,
    radius values, etc.

    It does NOT determine business logic.
    """

    def __init__(
        self,
        session: Session,
    ):

        self.repository = FacilityRepository(session)

        self._space_regex = re.compile(r"\s+")

        self._radius_pattern = re.compile(
            r"(?P<radius>\d+)\s?(km|kilometers?)",
            re.IGNORECASE,
        )

        self._limit_pattern = re.compile(
            r"(top|best)\s+(?P<limit>\d+)",
            re.IGNORECASE,
        )

        # -----------------------------
        # Load Cities
        # -----------------------------

        self._cities = {
            city.lower(): city
            for city in self.repository.get_all_cities()
            if city
        }

        # -----------------------------
        # Load Companies
        # -----------------------------

        self._companies = {
            company.lower(): company
            for company in self.repository.get_all_companies()
            if company
        }
        
        # -----------------------------
        # Load Facilities
        # -----------------------------
        
        self._facilities = {
            facility.lower(): facility
            for facility in self.repository.get_all_facility_names()
            if facility
        }
    
    # =====================================================
    # Public
    # =====================================================

    def parse(
        self,
        question: str,
    ) -> dict:

        normalized = self._normalize(question)

        return {

            "original_question": question,

            "normalized_question": normalized,

            "city": self._extract_city(normalized),

            "company": self._extract_company(normalized),

            "facility": self._extract_facility(normalized),

            "country": self._extract_country(normalized),

            "radius_km": self._extract_radius(normalized),

            "limit": self._extract_limit(normalized),
        }

    # =====================================================
    # Normalize
    # =====================================================

    def _normalize(
        self,
        question: str,
    ) -> str:

        question = question.lower().strip()

        question = self._space_regex.sub(
            " ",
            question,
        )

        return question

    # =====================================================
    # City
    # =====================================================

    def _extract_city(
        self,
        question: str,
    ) -> str | None:

        for city in sorted(
            self._cities.keys(),
            key=len,
            reverse=True,
        ):

            pattern = rf"\b{re.escape(city)}\b"

            if re.search(
                pattern,
                question,
                re.IGNORECASE,
            ):

                return self._cities[city]

        return None

    # =====================================================
    # Company
    # =====================================================

    def _extract_company(
        self,
        question: str,
    ) -> str | None:

        for company in sorted(
            self._companies.keys(),
            key=len,
            reverse=True,
        ):

            pattern = rf"\b{re.escape(company)}\b"

            if re.search(
                pattern,
                question,
                re.IGNORECASE,
            ):

                return self._companies[company]

        return None

    # =====================================================
    # Country
    # =====================================================

    def _extract_country(
        self,
        question: str,
    ) -> str | None:

        countries = [
            "Germany",
            "Netherlands",
            "Belgium",
            "France",
            "Luxembourg",
        ]

        question = question.lower()

        for country in countries:

            if country.lower() in question:

                return country

        return None

    # =====================================================
    # Radius
    # =====================================================

    def _extract_radius(
        self,
        question: str,
    ) -> int | None:

        match = self._radius_pattern.search(question)

        if not match:
            return None

        return int(
            match.group("radius")
        )

    # =====================================================
    # Limit
    # =====================================================

    def _extract_limit(
        self,
        question: str,
    ) -> int | None:

        match = self._limit_pattern.search(question)

        if not match:
            return None

        return int(
            match.group("limit")
        )

    # =====================================================
    # Compare Companies
    # =====================================================

    def extract_companies(
            self,
            question: str,
        ) -> tuple[str | None, str | None]:
            """
            Extract two companies from a comparison query.

            Examples

            Compare Microsoft vs Equinix

            NorthC against AtlasEdge

            Difference between Colt and NTT
            """

            normalized = self._normalize(question)

            companies = []

            for company in sorted(
                self._companies.keys(),
                key=len,
                reverse=True,
            ):

                pattern = rf"\b{re.escape(company)}\b"

                if re.search(
                    pattern,
                    normalized,
                    re.IGNORECASE,
                ):
                    companies.append(
                        self._companies[company]
                    )

            # Preserve order
            companies = list(dict.fromkeys(companies))

            if len(companies) >= 2:

                return (
                    companies[0],
                    companies[1],
                )

            if len(companies) == 1:

                return (
                    companies[0],
                    None,
                )

            return (
                None,
                None,
            )

    def _extract_facility(
        self,
        text: str,
    ) -> str | None:
        """
        Find a facility mentioned in the user question.

        Supports partial matching.
        """

        text = text.lower()

        for facility in self._facilities.values():

            facility_lower = facility.lower()

            # Exact match
            if facility_lower in text:
                return facility

            # Partial match
            words = facility_lower.split()

            matched = sum(
                1
                for word in words
                if len(word) > 3 and word in text
            )

            if matched >= 2:
                return facility

        return None