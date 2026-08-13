# ADR-010: FaceVis air quality — data source, charpack mapping, server-side token

- **Status:** accepted
- **Date:** 2026-08-12
- **Cycle:** cycle-011

## Context

The user asked for FaceVis to open a world map showing live air quality, let a visitor drive the robot's face from it (using the real FaceVis charpack assets), and have the robot explain the research's purpose (grounded in the actual paper) when the demo starts.

Investigation before writing code: read the FaceVis charpack archive's own scripts (`play_faces.py`, `facevis_demo.py`, `test_api.py`) and inspected the charpack files directly, confirming the selection mechanism is `character="<Charpack>/<Charpack><frame>"` (old Remote API's `set_face`) — and confirmed the Realtime API's `request_face_config(face_id=...)` uses the same `face_id` concept, so the migration in cycle-009 doesn't block this. Counted actual frames per air-quality charpack: `AirModerate` (1), `AirSensGroups` (3), `AirUnhealthy` (4), `AirHazard` (5), plus a generic `Airpollution` (2, unused here). No charpack exists for "Good" air quality — reasonable, since no visible symptoms is itself meaningful.

## Decision

1. **AQI → charpack mapping**: standard EPA AQI bands mapped onto the available charpacks — Good (0-50) → face reset (no charpack); Moderate (51-100) → `AirModerate`; Unhealthy for Sensitive Groups (101-150) → `AirSensGroups`; Unhealthy (151-200) → `AirUnhealthy`; Very Unhealthy + Hazardous (201-500) → `AirHazard`'s 5 frames, combined since no separate "Very Unhealthy" charpack exists. Frame selection within a band is proportional to position in that band's AQI range.
2. **WAQI (aqicn.org)** as the air-quality data source — its `/map/bounds` endpoint is purpose-built for "many stations for a map," matching the ask directly. Confirmed the general response shape via its `/feed/` endpoint with the public demo token (the `/map/bounds` endpoint itself needs a real registered token, which wasn't available to verify against — see `ASSUMPTIONS.md` A-014).
3. **The WAQI token never reaches the browser.** `GET /api/facevis/stations` proxies the WAQI call server-side; the frontend only ever talks to our own backend. Same reasoning as not exposing `OPENAI_API_KEY`/`FURHAT_AUTH_KEY` to the client.
4. **A plain link (`window.open`) to a static `/facevis` page**, not a single-page-app tab-switching UI — consistent with this project's existing static-HTML-per-page pattern (`index.html`, `admin.html`), and matches "opens a new tab" literally.
5. **Leaflet + OpenStreetMap tiles via CDN** — the first external CDN dependency in this project (every other page has been fully self-contained vanilla JS/CSS). Justified because a from-scratch world map renderer is out of scope, and the page already needs live internet access to fetch air-quality data regardless.

## Alternatives considered

- **Continuous facial parameter control** (`request_face_params`, ARKit-style blend shapes) instead of discrete charpack frames — rejected for this cycle: the user explicitly asked to use the existing charpack assets, and the real FaceVis research itself was built and evaluated using discrete pre-authored face states, not continuous parametric control. Tracked as a stretch goal in `BACKLOG.md`.
- **Other AQI providers** (OpenAQ, IQAir) — WAQI chosen for its map-oriented endpoint and because the source paper itself referenced IQAir's AQI categorisation guidelines, which WAQI's AQI scale also follows.

## Consequences

- Requires the user to obtain their own free WAQI API token (`WAQI_API_TOKEN` env var) — not provided by this project.
- Requires the `.charpack` files to be manually uploaded to the robot via its own web interface before this works live — unchanged from the original FaceVis project's own deployment process, not something this cycle's code can do remotely.
- The `/map/bounds` response parser is untested against a real successful response (only against the documented/recalled shape) — see `ASSUMPTIONS.md` A-014.
- The AQI→charpack mapping is a design choice, not something derived from the paper itself (the paper covers the *design process*, not a specific numeric mapping) — reasonable but worth the user's sign-off once they can see it live.
