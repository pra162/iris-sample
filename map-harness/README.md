# IRIS map first-load pilot

## Scope and missing production module

The available IRIS sample checkout has a Streamlit/PyDeck map but does **not** include the reported enterprise React/Kepler client, its complete frontend runtime, production style/tile configuration, or real BESS and peatland data adapters. A remote `git fetch` was attempted for the maintainer-updated baseline but was denied by the environment; this pilot therefore uses the locally available checkout. It reproduces the reported class of failure in a deterministic browser harness, not the exact missing production implementation. The production root cause still needs verification in the maintainer's React/Kepler runtime.

This is intentionally a small isolated harness under `map-harness/`. It does not alter the dashboard, access databases, use credentials, call a tile provider, or require production access.

## Requirements and setup

- Node.js 20 or newer and npm
- Python 3 for Playwright's local static fixture server
- Chromium installed through Playwright

From the repository root:

```sh
cd map-harness
npm ci
npx playwright install chromium
npm test
```

The Playwright config starts a local HTTP server on `127.0.0.1:4173`; tests run against local files and synthetic fixture assets only. To view the map manually, start a local server and open the page:

```sh
cd map-harness
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/index.html`. To exercise two tile failures followed by successful fallback, open `http://127.0.0.1:4173/index.html?failTiles=2`. To see the unrepaired race, open `http://127.0.0.1:4173/index.html?legacy=1`. The smoke page (`/smoke.html`) remains a dependency-free in-browser runner.

## Automated checks and evidence

`npm test` runs four Playwright checks:

1. Reproduce the missed style-ready event; assert the before-fix page remains blank, then assert initial style and both layers on the fixed page.
2. Verify BESS and peatland controls independently hide their respective features.
3. Fail the mock tile source twice and assert fallback recovery; fail all retries and assert a visible error, a visible basemap, and successful manual retry.
4. Measure first-style latency for three independent page loads and print each value and the mean.

The first test writes reproducible full-page browser captures to `screenshots/before-fix.png` and `screenshots/after-fix.png`. Playwright tests also produce result output and failure traces under `test-results/`. The `data-first-style-ms` measurement starts when the map harness is constructed and ends when the mocked style is displayed; it excludes tile readiness, fixture retrieval, and cold-start/browser installation overhead. Re-run the third check on the target machine to get that environment's comparison. Timing numbers are measurements, not a performance guarantee.

Latest Playwright run on macOS ARM64 Chromium: `4 passed (10.0s)`. The three first-style measurements were `24.9 ms, 25.9 ms, 25.8 ms` (mean `25.53 ms`). Reproduce with `npm test`; expected elapsed measurements vary with browser and host load.

## Fixture provenance, license, and limitations

`fixtures/bess.geojson` and `fixtures/peatland.geojson` are synthetic, locally authored test data, marked CC0-1.0 in each asset's metadata. Features have `geometry: null`: marker positions are schematic CSS placements and **not coordinates**. The fixture source date `2026-10-23` records the harness data version/date, not an observation or dataset publication date. Attribution is shown in the map and source table. No third-party geospatial data, map tiles, or basemap artwork is included. The drawn basemap itself is a local schematic mock and makes no geographic or national-coverage claim.

## Engineering note and safe integration

The harness models a lifecycle race where a style-ready event fires before a late listener is registered. The fix awaits style initialization directly and makes the styled basemap visible independently of tile readiness. Tile requests are modeled separately with bounded retries, an explicit fallback state, and a user-invokable retry after exhaustion. Keeping the basemap visible and exposing status avoids a silent grey failure. The mock uses authored SVG shapes rather than deploying a commercial map provider, accepting that it cannot validate vendor-specific style or tile behavior.

For safe IRIS integration, port the initialization sequencing and visible loading/error/retry behavior into the maintainer-owned React/Kepler application after obtaining its source and runtime. Keep actual source attribution, licenses, dates, coordinate reference systems, and tile-provider terms with their adapters; replace the synthetic GeoJSON only with permitted, provenance-documented fixtures. Run equivalent browser checks against the real client before any production rollout. Do not infer that this pilot fixes or deploys the absent enterprise frontend.

## Submission state

- Working isolated source and reproducible browser tests: included.
- Self-contained synthetic fixture assets: included.
- Before/after screenshots: captured by Playwright and included at the screenshot paths above.
- Exact production React/Kepler fix: unfinished because the target module is missing from the available checkout.
- Latest Playwright test output: 4 tests passed; see the three-run measurements above.
