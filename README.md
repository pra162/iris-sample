# 🏢 NRW Data Center Business Intelligence Platform

### AI-Powered Geospatial Business Intelligence for Data Center Site Selection and Infrastructure Analysis

The NRW Data Center Business Intelligence Platform is an AI-powered decision support system that combines geospatial analysis, infrastructure intelligence, renewable energy data, market intelligence, and conversational AI into a single interactive dashboard.

Built with **Python**, **PostgreSQL/PostGIS**, **GeoPandas**, **PyDeck**, **Streamlit**, and **OpenAI**, the platform enables users to evaluate data center locations through interactive GIS visualization, site scoring, and AI-assisted insights.

---

## Table of Contents

- [Overview](#overview)
- [Dashboard Preview](#dashboard-preview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [How It Works](#how-it-works)
- [Dashboard Modules](#dashboard-modules)
- [AI Advisor](#ai-advisor)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Dashboard](#running-the-dashboard)
- [Project Status](#current-project-status)
- [Roadmap](#roadmap)
- [Vision](#vision)

![Python]
![PostgreSQL]
![PostGIS]
![Streamlit]
![OpenAI]
![Status]

## Overview

Selecting an optimal location for a modern data center requires much more than available land.

Power infrastructure, renewable energy, electrical grid capacity, market activity, and surrounding infrastructure all influence the long-term viability of a site.

The NRW Data Center Business Intelligence Platform integrates multiple public infrastructure datasets into a unified PostgreSQL/PostGIS database and provides an interactive AI-powered dashboard for analyzing, comparing, and evaluating potential data center locations.

The platform combines:

- Geospatial Intelligence
- Infrastructure Analysis
- Site Scoring
- Market Intelligence
- AI-assisted Decision Support

# Key Features

## GIS Intelligence

✔ Interactive GIS Infrastructure Map

✔ Data Center Visualization

✔ High Voltage Substations

✔ Transformers

✔ Transmission Lines

✔ Renewable Energy Assets

---

## Business Intelligence

✔ KPI Dashboard

✔ Site Intelligence

✔ Site Score

✔ Market Intelligence

✔ News Intelligence

✔ Spatial Infrastructure Analysis

---

## Artificial Intelligence

✔ AI Advisor

✔ Natural Language Queries

✔ Executive Infrastructure Summaries

✔ Context-aware Responses

✔ Retrieval-Augmented Generation (RAG)

---

## Spatial Intelligence

✔ Power Readiness Analysis

✔ Renewable Energy Analysis

✔ Infrastructure Distance Calculations

✔ Land Value Integration

✔ Site Ranking

# System Architecture

```mermaid
flowchart TD

A[External Data Sources]

B[ETL Pipelines]

C[PostgreSQL + PostGIS]

D[Repository Layer]

E[Business Services]

F[Interactive Dashboard]

G[Site Intelligence]

H[News Intelligence]

I[AI Advisor]

J[Executive Decision Support]

A --> B
B --> C
C --> D
D --> E

E --> F
E --> G
E --> H

F --> I
G --> I
H --> I

I --> J
```
```

┌──────────────────────┐
│ External Data Sources│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    ETL Pipelines     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ PostgreSQL + PostGIS │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Repository Layer     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Business Services    │
└──────────┬───────────┘
           ▼
      ┌────┴────┐
      ▼         ▼
┌──────────┐ ┌──────────┐
│ GIS Map  │ │ News BI  │
└────┬─────┘ └────┬─────┘
     │            │
     └────┬───────┘
          ▼
┌──────────────────────┐
│ Site Intelligence    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ AI Advisor           │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ OpenAI GPT           │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Executive Insights   │
└──────────────────────┘
```
```                  

# Dashboard Modules

## Interactive GIS Map

Visualizes:

- Data Centers
- High Voltage Substations
- Transformers
- Renewable Energy Assets
- High Voltage Transmission Lines

---

## KPI Dashboard

Provides executive metrics for infrastructure assets, facilities, and renewable energy resources.

---

## Site Intelligence

Displays infrastructure proximity, renewable energy availability, land valuation, and technical site characteristics for the selected facility.

---

## Site Score

Calculates a unified infrastructure readiness score using spatial analysis and business intelligence metrics.

---

## News Intelligence

Aggregates recent industry news and links relevant articles to companies and facilities.

---

## AI Advisor

Provides conversational access to infrastructure intelligence using natural language.


# AI Advisor

The AI Advisor enables users to explore infrastructure intelligence using natural language.

Current capabilities

- Site Summaries
- Infrastructure Analysis
- Grid Readiness Evaluation
- Renewable Energy Analysis
- Executive Recommendations
- News Summaries

Upcoming

- Intent Detection
- Tool Routing
- Context Awareness
- LangGraph Agents
- Agentic RAG


# Technology Stack

## Backend

- Python
- SQLAlchemy
- PostgreSQL
- PostGIS

## GIS

- GeoPandas
- Shapely
- PyDeck

## Dashboard

- Streamlit

## AI

- OpenAI
- Retrieval-Augmented Generation (RAG)

## Data Processing

- Pandas
- JSON
- GeoJSON

nrw-dc-bi/
│
├── app/
│   ├── services/
│   ├── repositories/
│   ├── database/
│   ├── spatial/
│   ├── intelligence/
│   └── ai/
│
├── ui/
│
├── data/
│
├── scripts/
│
├── tests/
│
└── README.md


# Installation

## Prerequisites

- Python 3.12+
- PostgreSQL 17 + PostGIS
- uv (Python package manager)

Install uv if you don't already have it:

```bash
pip install uv
```

or

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Clone the Repository

```bash
git clone <repository-url>

cd nrw-dc-bi
```

---

## Create a Virtual Environment

```bash
uv venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
uv sync
```

If you're not using a `uv.lock` yet, then instead use:

```bash
uv pip install -r requirements.txt
```

---

## Configure Environment

```bash
cp .env.example .env
```

Update the database connection and OpenAI API key.

---

## Run Database Migrations

```bash
alembic upgrade head
```

---

## Start the Dashboard

```bash
streamlit run ui/app.py
```

The application will be available at:

```
http://localhost:8501
```

## Requirements

- Python 3.12+
- PostgreSQL 17
- PostGIS
- Git
- uv

# Running the Dashboard

```bash
streamlit run ui/app.py
```
# Current Project Status

## Completed

- Data Collection
- ETL Pipelines
- GIS Dashboard
- Interactive Map
- Site Intelligence
- Site Score
- News Intelligence
- AI Advisor
- Infrastructure Layers

## In Progress

- Context-aware AI
- Intent Detection
- Tool Routing
- LangGraph Integration

## Planned

- Multi-Agent AI
- Predictive Site Recommendations
- Investment Forecasting
- Voice Interface


# Roadmap

## Completed

- ETL Platform
- GIS Visualization
- Business Intelligence Dashboard
- AI Advisor
- News Intelligence

## Next

- Intent Detection
- Context-aware Responses
- Agentic RAG
- LangGraph Workflows

## Future

- Predictive Site Ranking
- Multi-Agent Decision Support
- Voice-enabled AI Advisor


# Vision

## UVP-Verbund procedure signal ingestion

The optional UVP procedure ingestor collects German environmental assessment
procedures that mention **data centers**, **substations**, or **battery energy
storage systems (BESS)** and upserts them into
`iris_staging.signal_ingest`. It uses the official, publicly accessible
[UVP-Verbund portal](https://www.uvp-verbund.de/), which indexes environmental
procedures published by the German states. As verified on 2026-10-28, it
exposes search results and procedure detail pages as HTML. Search results are
paginated with `page` query parameters; detail pages provide stable `docuuid`
identifiers, titles, result dates, descriptions, procedure categories, and
sometimes a machine-readable map bounding box in the `Raumbezug` section.

The separately operated [UVP-Portal des Bundes](https://www.uvp-portal.de/)
was also checked. Its current procedure search is a Drupal HTML page using the
`search_api_fulltext` GET field. On the verification date, searches for
`Rechenzentrum` and `Batteriespeicher` showed no matches; `Umspannwerk`
returned a small federal-portal result set, with the observed entries focused
on transmission-line procedures. UVP-Verbund was selected because its
state-level index returned direct data-center, substation, and BESS procedures
across German authorities. The federal portal is accessible, not assumed
obsolete; it is a less complete source for this particular nationwide
state-procedure scope.

### Mapping and geographic assumptions

* Search terms are `Rechenzentrum`, `Datacenter`, `Umspannwerk`,
  `Batteriespeicher`, and `BESS`. A record is retained only when its title,
  procedure description, or category matches the configured domain keywords.
  One procedure matching multiple types creates one row per type.
* The UVP `docuuid` is the source identifier. The detail page's `Zuletzt
  geändert` date is stored as `source_updated_at`; the search-card date is
  stored independently as `source_result_date`. `publication_date` is
  populated only when a publication / public-display date can be read from a
  procedure step. Decision dates and other event-date text are preserved in
  `raw_payload.procedure_dates`, not mislabeled as publication dates.
* The `Raumbezug` map's WGS84 bounding boxes are preserved in `source_bbox`.
  Their center is projected to EPSG:25832 and stored as a `Point` geometry,
  with `geometry_from_source_bbox_centroid` to make the approximation
  explicit. A centroid is not a surveyed project coordinate.
* Procedures categorized as `Ausländische Vorhaben` are excluded. Search
  results without map coordinates remain traceable with `geometry = NULL` and
  the `geometry_unresolved` quality flag. Malformed or out-of-range map
  coordinates are not converted; an `invalid_source_bbox` issue is emitted.
  No third-party geocoder is used. The optional `--provider` parameter can
  narrow results to a portal provider/state code (for example `nw`).
* The card date is a source result date, not guaranteed to be a publication
  date. If there is no explicit publication date, the field remains `NULL`.

### Run and configure

The project manifest already includes the needed HTTP, HTML, projection, and
PostgreSQL libraries (`requests`, `beautifulsoup4`, `pyproj`, and `psycopg`).
Install the project's dependencies in the usual way, for example:

```bash
uv sync
```

For a network-only demonstration (no database credentials required):

```bash
python -m app.commands.ingest_uvp_signals --dry-run --max-pages 1 \
  > /tmp/uvp-records.json
```

JSON records are written to stdout; the concise quality/error report is written
to stderr. For a database load, set `DATABASE_URL` in the process environment
(never commit credentials), then run:

```bash
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
python -m app.commands.ingest_uvp_signals --max-pages 5
```

The loader creates the `postgis` extension (if permitted), schema, and staging
table if absent. It requires PostgreSQL 16 with PostGIS 3.4 and a role allowed
to create the extension/schema/table or use an already-provisioned compatible
table. No production connection is required to run tests or the dry-run.
Configuration can be supplied through flags or environment variables:

| Setting | Default | Description |
|---|---|---|
| `UVP_BASE_URL` | `https://www.uvp-verbund.de` | Portal base URL; override for a fixture server |
| `UVP_MAX_PAGES` | `5` | Maximum search pages fetched for each search term |
| `UVP_REQUEST_TIMEOUT` | `25` | HTTP timeout in seconds |
| `UVP_REQUEST_DELAY_SECONDS` | `1` | Delay between requests to the public portal |
| `--since YYYY-MM-DD` | unset | Exclude results whose portal card date is older than this date |
| `--provider nw` | unset | Optional UVP-Verbund provider/state filter |

`--since` supports repeatable incremental ingestion but does not assume that
the portal's ranking is a strict change-data feed. Search results are still
walked up to the configured page limit. Network and malformed-page problems
are reported; the request adapter retries temporary HTTP failures. Empty
searches are recorded in the report without failing the run.

### Idempotency and validation

Rows are uniquely keyed by `(source_name, source_id, signal_type)` and use
PostgreSQL `ON CONFLICT DO UPDATE`, so re-running the same scrape refreshes
traceable source fields without duplicating rows. Useful checks after ingestion:

```sql
-- Volume, signal coverage, and geometry availability
SELECT signal_type, count(*) AS records,
       count(geometry) AS located,
       count(*) FILTER (WHERE geometry IS NULL) AS unresolved
FROM iris_staging.signal_ingest
WHERE source_name = 'uvp_verbund'
GROUP BY signal_type
ORDER BY signal_type;

-- Confirm point geometry and the expected SRID
SELECT count(*) AS invalid_or_wrong_srid
FROM iris_staging.signal_ingest
WHERE source_name = 'uvp_verbund'
  AND geometry IS NOT NULL
  AND (GeometryType(geometry) <> 'POINT' OR ST_SRID(geometry) <> 25832);

-- Confirm there are no duplicate source/type keys
SELECT source_name, source_id, signal_type, count(*)
FROM iris_staging.signal_ingest
WHERE source_name = 'uvp_verbund'
GROUP BY source_name, source_id, signal_type
HAVING count(*) > 1;

-- Review unlocated and approximate coordinates with source traceability
SELECT source_id, signal_type, title, source_url, quality_flags
FROM iris_staging.signal_ingest
WHERE source_name = 'uvp_verbund'
  AND (geometry IS NULL OR 'geometry_from_source_bbox_centroid' = ANY(quality_flags))
ORDER BY source_updated_at DESC NULLS LAST;
```

### Test, sample, and current quality notes

Run fixture-backed parser, pagination, domain filter, incremental filter, and
repeat-upsert contract tests with:

```bash
python -m unittest discover -s tests -p 'test_uvp_ingestion.py' -v
```

[`examples/uvp_public_sample.json`](examples/uvp_public_sample.json) contains
two sample staging rows from the publicly accessible Rohne BESS/substation
procedure. It has a source update date, no explicit publication date, and a
map bounding-box centroid in EPSG:25832. The source procedure's description
identifies the location at Gemarkung Rohne, Gemeinde Schleife.

Quality report for this sample:

* 1 source procedure, represented by 2 signal rows (BESS and substation).
* 1 source bounding box converted to an approximate centroid point.
* 0 explicit publication dates on this detail page; the source's
  `Zuletzt geändert` date is retained separately.
* 0 missing/invalid coordinates in this sample. Other procedures without map
  coordinates remain in staging with a visible unresolved flag.

[`examples/uvp_quality_report.json`](examples/uvp_quality_report.json) records
the corresponding bounded live dry-run performed on 2026-10-28 (one search
page per term). It found 36 procedures, filtered 9 outside the supported
domain/geographic scope, and produced 29 rows spanning all three signal types;
all 29 had source map bounds. The counts are a dated demonstration, not a
coverage estimate.

The portal is a government-hosted aggregation of procedures from German
authorities, not a complete register of every planned project. Search relevance
and authority-supplied descriptions vary. Search-page layout changes, record
updates, provider filtering, and the per-query page cap can affect coverage.
The map uses the source's bounds and the centroid is only a representative
point; a NULL point does not mean the underlying project has no location.

The long-term vision is to build an AI-powered decision support platform for data center planning and infrastructure investment.

By combining geospatial intelligence, power infrastructure, renewable energy, land valuation, market intelligence, and conversational AI, the platform enables users to evaluate and compare potential data center locations through natural language interaction.

The project is designed to evolve into a comprehensive executive decision-support system that assists planners, investors, and infrastructure specialists in identifying optimal data center locations.# iris-sample
