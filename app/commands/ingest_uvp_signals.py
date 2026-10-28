import argparse
import json
import logging
import math
import os
import sys
from dataclasses import asdict
from datetime import date

import psycopg

from app.loaders.uvp_signal_loader import (
    ensure_staging_table,
    normalize_database_url,
    upsert_records,
)
from app.scrapers.uvp.models import UvpRecord
from app.scrapers.uvp.scraper import BASE_URL, SEARCH_TERMS, UvpScraper


def _parse_date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Use YYYY-MM-DD for --since") from error


def _serialize_record(record: UvpRecord) -> dict[str, object]:
    value = asdict(record)
    for key in ("publication_date", "source_updated_at", "source_result_date"):
        date_value = value[key]
        value[key] = date_value.isoformat() if date_value else None
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest Data Center, Substation, and BESS procedures from UVP-Verbund."
    )
    parser.add_argument("--dry-run", action="store_true", help="Scrape and print JSON without writing to PostgreSQL.")
    parser.add_argument("--since", type=_parse_date_argument, help="Only ingest records with a source date on/after YYYY-MM-DD.")
    parser.add_argument("--provider", help="Optional UVP-Verbund provider/state filter, such as nw.")
    parser.add_argument("--max-pages", type=int, default=int(os.getenv("UVP_MAX_PAGES", "5")))
    parser.add_argument("--timeout", type=float, default=float(os.getenv("UVP_REQUEST_TIMEOUT", "25")))
    parser.add_argument(
        "--request-delay",
        type=float,
        default=float(os.getenv("UVP_REQUEST_DELAY_SECONDS", "1")),
        help="Delay between portal requests in seconds.",
    )
    parser.add_argument("--base-url", default=os.getenv("UVP_BASE_URL", BASE_URL))
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    if args.max_pages < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
        print("ERROR --max-pages must be at least 1 and --timeout must be positive.", file=sys.stderr)
        return 2
    if not math.isfinite(args.request_delay) or args.request_delay < 0:
        print("ERROR --request-delay must be a non-negative finite number.", file=sys.stderr)
        return 2
    scraper = UvpScraper(
        base_url=args.base_url,
        timeout=args.timeout,
        max_pages=args.max_pages,
        provider=args.provider,
        since=args.since,
        request_delay=args.request_delay,
    )
    scraped = scraper.scrape()

    if args.dry_run:
        json.dump(
            [_serialize_record(record) for record in scraped.records],
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        written = 0
    else:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("ERROR Set DATABASE_URL before running without --dry-run.", file=sys.stderr)
            return 2
        try:
            with psycopg.connect(normalize_database_url(database_url)) as connection:
                ensure_staging_table(connection)
                written = upsert_records(connection, scraped.records)
        except psycopg.Error as error:
            logging.exception("Could not write UVP records to iris_staging.signal_ingest")
            print(f"ERROR PostgreSQL/PostGIS write failed: {error}", file=sys.stderr)
            return 2

    unresolved = sum("geometry_unresolved" in record.quality_flags for record in scraped.records)
    approximate = sum(
        "geometry_from_source_bbox_centroid" in record.quality_flags
        for record in scraped.records
    )
    report = {
        "source": "UVP-Verbund",
        "source_url": args.base_url,
        "queries": list(SEARCH_TERMS),
        "pages_fetched": scraped.pages_fetched,
        "procedures_found": scraped.procedures_found,
        "source_procedures_filtered_out": max(
            0,
            scraped.procedures_found
            - len({record.source_id for record in scraped.records}),
        ),
        "staging_rows_upserted": written,
        "records_by_signal_type": {
            signal_type: sum(record.signal_type == signal_type for record in scraped.records)
            for signal_type in ("DATA_CENTER", "SUBSTATION", "BESS")
        },
        "geometry_bbox_centroids": approximate,
        "geometry_unresolved": unresolved,
        "records_missing_description": sum(
            "missing_description" in record.quality_flags for record in scraped.records
        ),
        "records_missing_source_date": sum(
            "source_date_unavailable" in record.quality_flags for record in scraped.records
        ),
        "records_with_invalid_coordinates": sum(
            "invalid_source_bbox" in record.quality_flags for record in scraped.records
        ),
        "empty_queries": scraped.empty_queries,
        "issues": [asdict(issue) for issue in scraped.issues],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
    return 2 if any(issue.code == "search_request_failed" for issue in scraped.issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
