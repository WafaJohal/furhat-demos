# ADR-011: FaceVis map — Plotly (server-rendered) instead of Leaflet/OSM

- **Status:** accepted
- **Date:** 2026-08-12
- **Cycle:** cycle-011 (follow-up)

## Context

ADR-010 chose Leaflet + OpenStreetMap tiles for the FaceVis map. In practice the map rendered incorrectly in the user's actual Chrome browser (misaligned/duplicated tiles). A `ResizeObserver`-based fix was tried and verified in this session's own browser pane, but did not resolve the issue on the user's machine, and the underlying cause was never confirmed. The user then asked to drop OpenStreetMap entirely and use a Python data-vis library instead: "I dont think you should show OSM. instead you could use a datavis library in python, no?"

## Decision

Replace the Leaflet/OSM tile map with a **server-rendered Plotly `Scattergeo` figure**:

- `GET /facevis` now builds the page dynamically (`render_facevis_page()` in `src/furhat_demos/facevis/map_page.py`) instead of serving a static `facevis.html`. Air-quality stations are fetched server-side and embedded directly into the page — `GET /api/facevis/stations` is removed as it's no longer needed by the frontend.
- Plotly's own world map (via its bundled shapefile-derived geography, `projection_type="natural earth"`) replaces OpenStreetMap tiles, removing the CDN tile dependency and the Leaflet sizing bug's entire code path.
- `plotly.graph_objects.Scattergeo` chosen over `plotly.express` specifically to avoid pulling in `pandas` as a dependency.
- Clicking a marker still POSTs to `/api/facevis/set_air_quality` (unchanged) via Plotly's `plotly_click` event, using each point's `customdata` (the station's AQI) — same face-driving behavior as before, just wired to Plotly's event model instead of Leaflet's marker click.
- `air_quality.py`'s AQI→charpack mapping (ADR-010) is unchanged; it was only reused for a second time (map marker color) via the new `aqi_category_color`/`aqi_category_label` functions, refactored out of the previously face-only `_AQI_CATEGORIES` table.

## Alternatives considered

- **Keep Leaflet, fix the sizing bug properly** — rejected: the bug wasn't reproducible in this session's own browser, a second fix attempt (`ResizeObserver`) still didn't resolve it on the user's machine, and the user's own preference had shifted away from an OSM-tile map regardless of the bug.
- **Keep a map, swap only the tile provider** — not what was asked; the user's ask was specifically to move to a Python data-vis library, not just a different map provider.
- **`plotly.express.scatter_geo`** — rejected to avoid adding `pandas` as a dependency purely for a DataFrame wrapper around a list of points.

## Consequences

- One fewer client-side dependency (no Leaflet JS/CSS from a CDN); Plotly's JS is still loaded from a CDN (`include_plotlyjs="cdn"`) inside the generated page.
- `/facevis` is no longer a static file — it now depends on the same server-side WAQI fetch that previously only backed `/api/facevis/stations`, so a WAQI failure now surfaces as an in-page banner on `/facevis` itself rather than a separate JSON 502.
- The map's visual style (built-in Plotly geography, not OSM road/place detail) is coarser than a tile-based map — acceptable per the user's own request to move away from OSM.
