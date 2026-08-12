# Cycle 011 — FaceVis: world map, live air quality, charpack face, paper-grounded intro

- **Date finalized:** 2026-08-12
- **Branch:** `feat/facevis-air-quality`
- **Version:** `0.3.0` → `0.3.1` (bump: patch — backward-compatible addition)

## Plan (as approved)
- **Scope:** `/facevis` map page (Leaflet + OpenStreetMap) opened in a new tab from the main page's Air Quality option; `GET /api/facevis/stations` proxying live WAQI data server-side; `POST /api/facevis/set_air_quality` mapping AQI → a real FaceVis `.charpack` frame via `request_face_config`; the facevis intro line replaced with content grounded in the actual research paper.
- **Files touched:** `src/furhat_demos/facevis/{__init__.py,air_quality.py,content.py}` (new), `control.py` (`set_face` on `DemoController`/`FurhatRealtimeClient`, updated intro), `config.py` (`WAQI_API_TOKEN_ENV_VAR`), `webui/app.py` (`/facevis` route, 2 new endpoints, injectable `stations_fetcher`), `webui/static/{facevis.html (new), index.html}`, `pyproject.toml` (no new deps — `httpx`/stdlib `math` only).
- **Tests:** `aqi_to_face_id` tested exhaustively against hand-computed expected values across every category boundary; `fetch_stations` against a fake HTTP client; `set_face` (success, reset, both failure paths, fail-soft); endpoint tests via `stations_fetcher`/`controller` DI, fully offline.

## Assumptions added
- **A-014** (new): WAQI's `/map/bounds` response shape is recalled/documented, not empirically verified — only the `/feed/` endpoint's general envelope was confirmed live (via WAQI's public demo token; `/map/bounds` needs a real registered token, unavailable here).
- **A-015** (new): the AQI-to-charpack mapping is this cycle's own design choice, not derived from the paper (which describes the design *process*, not a numeric mapping) — needs the user's sign-off once seen live.

## Decisions made
- **ADR-010** — AQI-to-charpack mapping, WAQI as the data source, server-side token proxying, plain-link-to-static-page instead of an SPA, and the first CDN dependency in this project (Leaflet).

## Test & coverage results
- Tests: 109/109 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Before writing any code: read the FaceVis dissertation chapter (`assets/schombs2025dis.pdf`, gitignored — large reference PDF, not committed) for the intro content and concrete PM2.5 design details; inspected the actual `FaceVis_charpack.zip` archive (also gitignored, in `assets/`) directly — extracted and counted real frames per air-quality charpack (`AirModerate`: 1, `AirSensGroups`: 3, `AirUnhealthy`: 4, `AirHazard`: 5), and confirmed the `character="<charpack>/<charpack><frame>"` selection format from the original project's own `play_faces.py`/`facevis_demo.py` scripts. Confirmed the Realtime API's `request_face_config(face_id=...)` carries the same `face_id` concept forward from the old Remote API's `set_face(character=...)`, so cycle-009's migration doesn't block this.
- **Real bug found and fixed via manual browser testing** (not just passing unit tests): the FaceVis map page initially showed a dark background bleeding through around the map — same class of contrast bug as cycle-001's index.html, from relying on the browser's default dark color-scheme instead of setting explicit colors. Fixed with explicit `background`/`color` on `html, body` and the `#map` container, plus `color-scheme: light`.
- Investigated a second apparent bug (map tiles not filling the container) using `javascript_tool` to inspect the live DOM/Leaflet state directly rather than guessing from screenshots — turned out to be correct behavior, not a bug: at zoom level 2, the rendered world map (1024×1024px) is narrower than the 1280×672 viewport, so background is visible beyond its edges by design. Worth recording as a reminder that not every visual gap in a screenshot is a bug — verify against the actual DOM state before "fixing" something that isn't broken.
- Neither the live WAQI `/map/bounds` endpoint (no registered token available) nor the real robot/charpack upload could be tested end-to-end in this environment — both flagged as the top `BACKLOG.md` item for the user to verify.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user

## Follow-up (post-plan, before merge)
- The Leaflet map rendered incorrectly in the user's real Chrome (misaligned/duplicated tiles). A `ResizeObserver`-based fix was tried and verified working in this session's own browser, but the user reported it was still broken on their end; the root cause was never confirmed.
- The user then asked to drop OpenStreetMap entirely in favor of a Python data-vis library. Reworked `/facevis` into a server-rendered Plotly (`Scattergeo`) page: `render_facevis_page()` in the new `facevis/map_page.py`, `GET /facevis` now builds the page dynamically instead of serving a static file, `GET /api/facevis/stations` removed (no longer needed — the page fetches server-side), `webui/static/facevis.html` deleted, `plotly` added as a dependency. `air_quality.py` refactored so its AQI-band table (`AqiCategory`) is now the shared source for both the robot's charpack selection and the map's marker color/label (`aqi_category_color`/`aqi_category_label`), reused by neither module owning the other's concern.
- See ADR-011 for the full reasoning. No version bump for this follow-up — same unmerged PR/cycle, consistent with the earlier `ResizeObserver` commit on this branch.
- Verified in the Browser pane: the Plotly map renders a clean world projection with no OSM dependency; the error banner correctly shows when `WAQI_API_TOKEN` is unset.
- Tests: 119/119 passed. Coverage: 100% (unchanged).
