import json
import math
import re
from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup, Tag

from app.scrapers.uvp.models import SearchResult, UvpIssue

DATE_FORMATS = ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y")
COORDINATE_PATTERN = re.compile(r"\bvar\s+coords\s*=\s*(\[.*?\])\s*;", re.DOTALL)
DOCUUID_PATTERN = re.compile(r"(?:\?|&)docuuid=([0-9a-f-]{36})(?:&|$)", re.IGNORECASE)

SIGNAL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "DATA_CENTER": (
        "rechenzentrum",
        "rechenzentren",
        "datacenter",
        "data center",
        "data centre",
    ),
    "SUBSTATION": (
        "umspannwerk",
        "umspannanlage",
        "schaltanlage",
        "umspannstation",
    ),
    "BESS": (
        "batteriespeicher",
        "bess",
        "battery energy storage",
        "großbatterie",
        "grossbatterie",
    ),
}


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for candidate in re.findall(r"\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}", value):
        for date_format in DATE_FORMATS:
            try:
                return datetime.strptime(candidate, date_format).date()
            except ValueError:
                continue
    return None


def classify_signals(text: str) -> list[str]:
    normalized = text.casefold()
    return [
        signal_type
        for signal_type, keywords in SIGNAL_KEYWORDS.items()
        if any(
            re.search(r"\bbess\b", normalized)
            if keyword == "bess"
            else keyword in normalized
            for keyword in keywords
        )
    ]


def parse_search_results(
    html: str,
    page_url: str,
) -> tuple[list[SearchResult], bool]:
    soup = BeautifulSoup(html, "html.parser")
    results_container = soup.select_one("#results")
    if results_container is None:
        raise ValueError("Search response has no #results container; portal markup may have changed")

    results: list[SearchResult] = []
    seen_ids: set[str] = set()
    for card in results_container.select("div.teaser-data.search"):
        link = card.select_one('a[href*="docuuid="]')
        if link is None:
            continue
        match = DOCUUID_PATTERN.search(link.get("href", ""))
        title = " ".join(link.get_text(" ", strip=True).split())
        if match is None or not title:
            continue
        source_id = match.group(1).lower()
        if source_id in seen_ids:
            continue
        seen_ids.add(source_id)

        category_element = card.select_one(".helper.text .text")
        date_element = card.select_one(".helper.date")
        teaser_element = card.select_one("p.data-text")
        results.append(
            SearchResult(
                source_id=source_id,
                title=title,
                source_url=urljoin(page_url, link["href"]),
                category=" ".join(category_element.get_text(" ", strip=True).split())
                if category_element
                else None,
                teaser=" ".join(teaser_element.get_text(" ", strip=True).split())
                if teaser_element
                else None,
                result_date=parse_date(date_element.get_text(" ", strip=True))
                if date_element
                else None,
            )
        )

    current_page = int(parse_qs(urlparse(page_url).query).get("page", ["1"])[0])
    linked_pages = []
    for link in results_container.select('a[href*="page="]'):
        page_values = parse_qs(urlparse(link.get("href", "")).query).get("page", [])
        if page_values and page_values[0].isdigit():
            linked_pages.append(int(page_values[0]))
    has_next_page = any(page > current_page for page in linked_pages)
    return results, has_next_page


def _section_text(soup: BeautifulSoup, heading_text: str) -> str | None:
    heading = soup.find(
        lambda element: isinstance(element, Tag)
        and element.name in {"h2", "h3", "h4"}
        and " ".join(element.get_text(" ", strip=True).split()).casefold()
        == heading_text.casefold()
    )
    if heading is None:
        return None
    row = heading.find_parent("div", class_="row")
    if row is None:
        return None
    text_parts = []
    for element in row.select("p, .helper .text"):
        text = " ".join(element.get_text(" ", strip=True).split())
        if text:
            text_parts.append(text)
    return " ".join(dict.fromkeys(text_parts)) or None


def _parse_bbox(html: str) -> tuple[dict[str, float] | None, str | None]:
    match = COORDINATE_PATTERN.search(html)
    if match is None:
        return None, None
    try:
        bounds: Any = json.loads(match.group(1))
        if not isinstance(bounds, list) or not bounds:
            raise ValueError("empty coordinates array")
        west = min(float(bound["westBoundLongitude"]) for bound in bounds)
        south = min(float(bound["southBoundLatitude"]) for bound in bounds)
        east = max(float(bound["eastBoundLongitude"]) for bound in bounds)
        north = max(float(bound["northBoundLatitude"]) for bound in bounds)
        if not all(math.isfinite(value) for value in (west, south, east, north)):
            raise ValueError("non-finite coordinate")
        if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
            raise ValueError("coordinate bounds are outside valid longitude/latitude ranges")
        if west == east == 0 or south == north == 0:
            raise ValueError("coordinate bounds contain an invalid zero location")
        return {
            "west": west,
            "south": south,
            "east": east,
            "north": north,
        }, None
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        return None, str(error)


def parse_detail_page(
    html: str,
) -> tuple[dict[str, Any], list[UvpIssue]]:
    soup = BeautifulSoup(html, "html.parser")
    title_element = soup.select_one(".detail h1")
    title = (
        " ".join(title_element.get_text(" ", strip=True).split())
        if title_element
        else None
    )
    description = _section_text(soup, "Allgemeine Vorhabenbeschreibung")
    category = _section_text(soup, "UVP-Kategorie")
    room_text = _section_text(soup, "Raumbezug")
    changed = None
    for element in soup.select(".helper.date"):
        text = " ".join(element.get_text(" ", strip=True).split())
        if "zuletzt geändert" in text.casefold():
            changed = parse_date(text)
            break

    procedure_dates: list[dict[str, str]] = []
    publication_date = None
    for heading in soup.select(".detail h2, .detail h3, .detail h4"):
        label = " ".join(heading.get_text(" ", strip=True).split())
        if not label or label.casefold() in {
            "allgemeine vorhabenbeschreibung",
            "uvp-kategorie",
            "raumbezug",
            "adressen",
        }:
            continue
        following = heading.find_parent("div", class_="columns")
        date_text = None
        if following is not None:
            for sibling in heading.find_all_next(["p", "h2", "h3", "h4"], limit=2):
                if sibling.name in {"h2", "h3", "h4"}:
                    break
                candidate = " ".join(sibling.get_text(" ", strip=True).split())
                if candidate:
                    date_text = candidate
                    break
        if date_text and parse_date(date_text):
            procedure_dates.append({"label": label, "date_text": date_text})
            if publication_date is None and re.search(
                r"veröffentlich|bekanntmachung|öffentliche auslegung|auslegung",
                label,
                re.IGNORECASE,
            ):
                publication_date = parse_date(date_text)

    bbox, bbox_error = _parse_bbox(html)
    issues: list[UvpIssue] = []
    if bbox_error:
        issues.append(
            UvpIssue(
                code="invalid_source_bbox",
                message=f"Could not use the source Raumbezug coordinates: {bbox_error}",
            )
        )
    return {
        "title": title,
        "description": description,
        "category": category,
        "room_text": room_text,
        "source_updated_at": changed,
        "publication_date": publication_date,
        "procedure_dates": procedure_dates,
        "source_bbox": bbox,
    }, issues
