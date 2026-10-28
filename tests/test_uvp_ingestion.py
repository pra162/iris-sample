import unittest
from datetime import date
from pathlib import Path

import requests

from app.loaders.uvp_signal_loader import UPSERT_SIGNAL, upsert_records
from app.scrapers.uvp.models import UvpRecord
from app.scrapers.uvp.parser import (
    classify_signals,
    parse_detail_page,
    parse_search_results,
)
from app.scrapers.uvp.scraper import UvpScraper

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureResponse:
    def __init__(self, text: str, url: str) -> None:
        self.text = text
        self.url = url

    def raise_for_status(self) -> None:
        return None


class FixtureSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.calls: list[str] = []

    def mount(self, prefix: str, adapter: object) -> None:
        return None

    def get(self, url: str, params: dict | None = None, timeout: float = 0) -> FixtureResponse:
        from urllib.parse import urlencode

        if params:
            page_url = f"{url}?{urlencode(params)}"
        else:
            page_url = url
        self.calls.append(page_url)
        if "freitextsuche" in url:
            if params and params.get("page") == 1:
                body = (FIXTURES / "uvp_search_results.html").read_text(encoding="utf-8")
            else:
                body = (FIXTURES / "uvp_search_empty.html").read_text(encoding="utf-8")
        else:
            body = (FIXTURES / "uvp_procedure_detail.html").read_text(encoding="utf-8")
        return FixtureResponse(body, page_url)


class FailingSession(FixtureSession):
    def get(self, url: str, params: dict | None = None, timeout: float = 0) -> FixtureResponse:
        raise requests.ConnectionError("fixture connection failure")


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str, parameters: tuple | None = None) -> None:
        self.connection.executed.append((query, parameters))


class FakeConnection:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple | None]] = []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)


class UvpParserTests(unittest.TestCase):
    def test_search_results_extract_metadata_deduplicate_and_follow_pagination(self) -> None:
        url = "https://www.uvp-verbund.de/freitextsuche?q=Batteriespeicher&page=1"
        fixture = (FIXTURES / "uvp_search_results.html").read_text(encoding="utf-8")

        results, has_next_page = parse_search_results(fixture, url)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source_id, "c61afee1-9390-499e-9ee2-8dad2e9a1636")
        self.assertEqual(results[0].result_date, date(2026, 2, 15))
        self.assertIn("Gemarkung Rohne", results[0].teaser or "")
        self.assertTrue(has_next_page)

    def test_empty_search_is_a_valid_empty_result(self) -> None:
        fixture = (FIXTURES / "uvp_search_empty.html").read_text(encoding="utf-8")

        results, has_next_page = parse_search_results(
            fixture,
            "https://www.uvp-verbund.de/freitextsuche?q=BESS",
        )

        self.assertEqual(results, [])
        self.assertFalse(has_next_page)

    def test_detail_extracts_publication_date_source_update_and_bbox(self) -> None:
        fixture = (FIXTURES / "uvp_procedure_detail.html").read_text(encoding="utf-8")
        detail, issues = parse_detail_page(fixture)

        self.assertEqual(detail["source_updated_at"], date(2026, 2, 16))
        self.assertEqual(detail["publication_date"], date(2026, 2, 1))
        self.assertEqual(detail["source_bbox"]["west"], 14.462320804595947)
        self.assertEqual(detail["category"], "Forstliche und landwirtschaftliche Vorhaben")
        self.assertEqual(issues, [])

    def test_invalid_source_coordinates_are_reported_and_not_used(self) -> None:
        fixture = (FIXTURES / "uvp_procedure_detail.html").read_text(encoding="utf-8")
        fixture = fixture.replace('"westBoundLongitude":14.462320804595947', '"westBoundLongitude":999')

        detail, issues = parse_detail_page(fixture)

        self.assertIsNone(detail["source_bbox"])
        self.assertEqual(issues[0].code, "invalid_source_bbox")

    def test_classification_filters_noise_and_matches_three_domains(self) -> None:
        text = "Neues Rechenzentrum mit Batteriespeicher und Umspannwerk"

        self.assertEqual(classify_signals(text), ["DATA_CENTER", "SUBSTATION", "BESS"])
        self.assertEqual(classify_signals("Besserer Lärmschutz am Standort"), [])


class UvpScraperTests(unittest.TestCase):
    def test_scrape_deduplicates_across_queries_and_produces_typed_records(self) -> None:
        session = FixtureSession()
        scraper = UvpScraper(
            session=session,  # type: ignore[arg-type]
            max_pages=2,
            request_delay=0,
        )

        result = scraper.scrape()

        self.assertEqual(result.procedures_found, 1)
        self.assertEqual(result.pages_fetched, 10)
        self.assertEqual(len(result.records), 2)
        self.assertEqual(
            {record.signal_type for record in result.records},
            {"SUBSTATION", "BESS"},
        )
        self.assertEqual(len([call for call in session.calls if "trefferanzeige" in call]), 1)
        self.assertTrue(
            all("geometry_from_source_bbox_centroid" in record.quality_flags for record in result.records)
        )
        self.assertTrue(all(record.source_updated_at == date(2026, 2, 16) for record in result.records))
        self.assertTrue(all(record.source_result_date == date(2026, 2, 15) for record in result.records))
        self.assertAlmostEqual(result.records[0].geometry_x or 0, 878710.118, places=2)
        self.assertAlmostEqual(result.records[0].geometry_y or 0, 5725373.733, places=2)

    def test_since_excludes_older_cards_before_detail_request(self) -> None:
        session = FixtureSession()
        scraper = UvpScraper(
            session=session,  # type: ignore[arg-type]
            max_pages=1,
            since=date(2026, 3, 1),
            request_delay=0,
        )

        result = scraper.scrape()

        self.assertEqual(result.records, [])
        self.assertEqual(result.procedures_found, 0)
        self.assertFalse(any("trefferanzeige" in call for call in session.calls))

    def test_network_failures_are_reported_without_silent_success(self) -> None:
        scraper = UvpScraper(session=FailingSession(), max_pages=1, request_delay=0)  # type: ignore[arg-type]

        result = scraper.scrape()

        self.assertEqual(result.records, [])
        self.assertEqual(len(result.issues), 5)
        self.assertTrue(all(issue.code == "search_request_failed" for issue in result.issues))


class UvpLoaderTests(unittest.TestCase):
    def test_repeated_upserts_use_database_conflict_key(self) -> None:
        record = UvpRecord(
            source_id="c61afee1-9390-499e-9ee2-8dad2e9a1636",
            title="Batteriespeicher mit Umspannwerk Gemarkung Rohne",
            signal_type="BESS",
            source_url="https://www.uvp-verbund.de/trefferanzeige?docuuid=c61afee1-9390-499e-9ee2-8dad2e9a1636",
            publication_date=None,
            source_updated_at=date(2026, 2, 16),
            source_result_date=date(2026, 2, 16),
            location_text="Gemarkung Rohne, Gemeinde Schleife",
            source_bbox={"west": 14.46, "south": 51.55, "east": 14.47, "north": 51.56},
            geometry_x=878710.1,
            geometry_y=5725373.7,
            raw_payload={"description": "Public-source fixture"},
            quality_flags=["geometry_from_source_bbox_centroid"],
        )
        connection = FakeConnection()

        self.assertEqual(upsert_records(connection, [record]), 1)
        self.assertEqual(upsert_records(connection, [record]), 1)

        upserts = [query for query, _ in connection.executed if query and "INSERT INTO" in query]
        self.assertEqual(len(upserts), 2)
        self.assertIn(
            "ON CONFLICT (source_name, source_id, signal_type) DO UPDATE",
            UPSERT_SIGNAL,
        )
        self.assertEqual(UPSERT_SIGNAL.count("%s"), len(connection.executed[0][1]))
        self.assertEqual(connection.executed[0][1][14].obj, {"description": "Public-source fixture"})


if __name__ == "__main__":
    unittest.main()
