import logging
import math
import time
from datetime import date
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.scrapers.uvp.models import (
    SearchResult,
    UvpIssue,
    UvpRecord,
    UvpScrapeResult,
)
from app.scrapers.uvp.parser import (
    classify_signals,
    parse_detail_page,
    parse_search_results,
)

logger = logging.getLogger(__name__)
SEARCH_TERMS = ("Rechenzentrum", "Datacenter", "Umspannwerk", "Batteriespeicher", "BESS")
BASE_URL = "https://www.uvp-verbund.de"


class UvpScraper:
    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 25,
        max_pages: int = 5,
        provider: str | None = None,
        since: date | None = None,
        session: requests.Session | None = None,
        request_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_pages = max_pages
        self.provider = provider
        self.since = since
        self.request_delay = request_delay
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "iris-sample-uvp-ingestor/1.0 (public data ingestion; contact: project maintainers)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _get(self, url: str, params: dict[str, Any] | None = None) -> str:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        time.sleep(self.request_delay)
        return response.text

    def scrape(self) -> UvpScrapeResult:
        result = UvpScrapeResult()
        candidates: dict[str, tuple[SearchResult, set[str]]] = {}

        for query in SEARCH_TERMS:
            page = 1
            query_has_results = False
            while page <= self.max_pages:
                params: dict[str, str | int] = {"q": query, "rank": "date", "page": page}
                if self.provider:
                    params["provider"] = self.provider
                url = urljoin(self.base_url + "/", "freitextsuche")
                try:
                    html = self._get(url, params=params)
                    result.pages_fetched += 1
                    page_url = requests.Request("GET", url, params=params).prepare().url
                    page_results, has_next = parse_search_results(html, page_url or url)
                except (requests.RequestException, ValueError) as error:
                    result.issues.append(
                        UvpIssue(
                            code="search_request_failed",
                            message=f"Query {query!r}, page {page}: {error}",
                            query=query,
                        )
                    )
                    logger.error("UVP search failed for %s page %s: %s", query, page, error)
                    break

                if not page_results:
                    if not query_has_results:
                        result.empty_queries.append(query)
                    break
                query_has_results = True
                for search_result in page_results:
                    if search_result.result_date and self.since and search_result.result_date < self.since:
                        continue
                    if search_result.source_id not in candidates:
                        candidates[search_result.source_id] = (search_result, set())
                    candidates[search_result.source_id][1].add(query)
                if not has_next:
                    break
                page += 1

        result.procedures_found = len(candidates)
        for source_id, (search_result, matched_queries) in candidates.items():
            result.issues.extend(
                self._get_records(
                    search_result=search_result,
                    matched_queries=matched_queries,
                    destination=result.records,
                )
            )
        return result

    def _get_records(
        self,
        search_result: SearchResult,
        matched_queries: set[str],
        destination: list[UvpRecord],
    ) -> list[UvpIssue]:
        issues: list[UvpIssue] = []
        detail: dict[str, Any] = {}
        record_quality: list[str] = []
        try:
            html = self._get(search_result.source_url)
            detail, detail_issues = parse_detail_page(html)
            issues.extend(
                UvpIssue(
                    code=issue.code,
                    message=issue.message,
                    source_id=search_result.source_id,
                )
                for issue in detail_issues
            )
            record_quality.extend(issue.code for issue in detail_issues)
        except (requests.RequestException, ValueError) as error:
            record_quality.append("detail_fetch_failed")
            issues.append(
                UvpIssue(
                    code="detail_fetch_failed",
                    message=f"Could not retrieve procedure detail: {error}",
                    source_id=search_result.source_id,
                )
            )
            logger.error("UVP detail request failed for %s: %s", search_result.source_id, error)

        title = detail.get("title") or search_result.title
        description = detail.get("description") or search_result.teaser
        category = detail.get("category") or search_result.category
        if "ausländische vorhaben" in {
            (category or "").casefold(),
            (search_result.category or "").casefold(),
        }:
            logger.info("Skipping foreign UVP procedure outside the German geographic scope: %s", search_result.source_id)
            return issues
        full_text = " ".join(part for part in (title, description, category) if part)
        signal_types = classify_signals(full_text)
        if not signal_types:
            logger.info("Skipping UVP result outside the configured signal domains: %s", search_result.source_id)
            return issues

        bbox = detail.get("source_bbox")
        geometry_x: float | None = None
        geometry_y: float | None = None
        if bbox:
            try:
                from pyproj import Transformer

                transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
                longitude = (bbox["west"] + bbox["east"]) / 2
                latitude = (bbox["south"] + bbox["north"]) / 2
                geometry_x, geometry_y = transformer.transform(longitude, latitude)
                if not all(math.isfinite(value) for value in (geometry_x, geometry_y)):
                    raise ValueError("projection returned a non-finite coordinate")
                record_quality.append("geometry_from_source_bbox_centroid")
            except (KeyError, ValueError, ImportError) as error:
                geometry_x = geometry_y = None
                record_quality.append("coordinate_projection_failed")
                issues.append(
                    UvpIssue(
                        code="coordinate_projection_failed",
                        message=f"Source bounds could not be projected to EPSG:25832: {error}",
                        source_id=search_result.source_id,
                    )
                )
        elif not any(flag == "invalid_source_bbox" for flag in record_quality):
            record_quality.append("geometry_unresolved")
            issues.append(
                UvpIssue(
                    code="geometry_unresolved",
                    message="The source detail page provided no usable Raumbezug coordinates; geometry is NULL.",
                    source_id=search_result.source_id,
                )
            )

        updated_at = detail.get("source_updated_at")
        result_date = search_result.result_date
        location_text = detail.get("room_text") or description
        if not description:
            record_quality.append("missing_description")
            issues.append(
                UvpIssue(
                    code="missing_description",
                    message="Neither the detail page nor the search result supplied a description.",
                    source_id=search_result.source_id,
                )
            )
        if not category:
            record_quality.append("missing_category")
            issues.append(
                UvpIssue(
                    code="missing_category",
                    message="The procedure category was not present in the search result or detail page.",
                    source_id=search_result.source_id,
                )
            )
        if not updated_at and not result_date and not detail.get("publication_date"):
            record_quality.append("source_date_unavailable")
            issues.append(
                UvpIssue(
                    code="source_date_unavailable",
                    message="No source result date or source update date was available.",
                    source_id=search_result.source_id,
                )
            )
        payload = {
            "category": category,
            "description": description,
            "location_text_basis": "Raumbezug section" if detail.get("room_text") else "procedure description",
            "search_queries": sorted(matched_queries),
            "procedure_dates": detail.get("procedure_dates", []),
            "source_updated_at": updated_at.isoformat() if updated_at else None,
            "source_result_date": result_date.isoformat() if result_date else None,
            "publication_date": (
                detail["publication_date"].isoformat()
                if detail.get("publication_date")
                else None
            ),
            "source_bbox": bbox,
        }
        for signal_type in signal_types:
            destination.append(
                UvpRecord(
                    source_id=search_result.source_id,
                    title=title,
                    signal_type=signal_type,
                    source_url=search_result.source_url,
                    publication_date=detail.get("publication_date"),
                    source_updated_at=updated_at,
                    source_result_date=result_date,
                    location_text=location_text,
                    source_bbox=bbox,
                    geometry_x=geometry_x,
                    geometry_y=geometry_y,
                    raw_payload=payload,
                    quality_flags=sorted(set(record_quality)),
                )
            )
        return issues
