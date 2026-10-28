from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class UvpRecord:
    source_id: str
    title: str
    signal_type: str
    source_url: str
    publication_date: date | None
    source_updated_at: date | None
    source_result_date: date | None
    location_text: str | None
    source_bbox: dict[str, float] | None
    geometry_x: float | None
    geometry_y: float | None
    raw_payload: dict[str, Any]
    quality_flags: list[str] = field(default_factory=list)


@dataclass
class UvpIssue:
    code: str
    message: str
    source_id: str | None = None
    query: str | None = None


@dataclass
class UvpScrapeResult:
    records: list[UvpRecord] = field(default_factory=list)
    issues: list[UvpIssue] = field(default_factory=list)
    pages_fetched: int = 0
    procedures_found: int = 0
    empty_queries: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SearchResult:
    source_id: str
    title: str
    source_url: str
    category: str | None
    teaser: str | None
    result_date: date | None
