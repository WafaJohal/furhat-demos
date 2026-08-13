# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-08-13
### Added
- FaceVis: clicking a station on the map now also has the robot speak the
  station's name and AQI category out loud (e.g. "In Delhi, the air quality
  index is 310 — Very Unhealthy / Hazardous."), alongside the existing
  face-driving behavior. `DemoController` gains a `say(text)` method,
  implemented fail-soft on `FurhatDemoController` like `set_face`.

## [0.3.1] - 2026-08-12
### Added
- FaceVis: `/facevis` page opens in a new tab when the Air Quality option is
  selected, server-rendering a Plotly world map (`render_facevis_page`) with
  live station data from WAQI/aqicn.org (`WAQI_API_TOKEN`, kept server-side;
  a Leaflet + OpenStreetMap version was tried first — see ADR-011 for why it
  was replaced). `POST /api/facevis/set_air_quality` maps an AQI value to a
  real FaceVis `.charpack` frame (`aqi_to_face_id`) and drives the robot's
  face via `request_face_config`/`request_face_reset`.
- The FaceVis demo's spoken intro is now grounded in the actual research
  paper ("I can feel the risks by looking at the robot face", Schömbs,
  Goncalves & Johal, DIS '25) instead of a placeholder line.
- `DemoController.set_face()` — new method alongside `start_demo()`, fails
  soft (logs and continues) like the existing voice/attend-user handling.

See ADR-010 for the AQI-to-charpack mapping and data-source reasoning, and
ADR-011 for the Leaflet-to-Plotly map pivot.

## [0.3.0] - 2026-08-12
### Removed
- **Breaking**: the "Wafa Johal" persona/option (button, intro line, system
  prompt, bio doc) — the opendemo demo now offers only `guide`.

### Added
- Admin PDF upload: a new `/admin` page (linked from the main page, not
  password-protected) to upload PDFs into the Open Day Q&A's knowledge base.
  `POST /api/admin/documents` extracts text (`pypdf`) and saves it alongside
  the Handbook content — `QAEngine` picks it up automatically. `GET`/`DELETE
  /api/admin/documents` list/remove uploads. See ADR-009.

## [0.2.0] - 2026-08-12
### Changed
- **Breaking**: migrated the robot connection from `furhat_remote_api` (REST,
  port 54321, no auth) to `furhat_realtime_api.FurhatClient` (WebSocket, port
  9000, built-in `auth_key`). The real robot/Virtual only had the Realtime
  API enabled — the old Remote API's port was never going to accept a
  connection regardless of network setup. See ADR-008.
- `config.build_controller()` removed (was unused by the app; superseded by
  `RobotConnection`). `FurhatDemoController` now takes a `FurhatRealtimeClient`
  instead of the old `RemoteApi`.
- Voice selection collapses to one `request_voice_config(language="en-US")`
  call, replacing the old manual list-voices/filter/set-voice dance.
- Added `request_attend_user()` on every `start_demo()` so the robot looks at
  the visitor.
- `listen()`'s sentinel handling simplified: the Realtime API returns a plain
  string (`""` on no speech) instead of `SILENCE`/`INTERRUPTED`/`FAILED`.

### Added
- Auth-key support: `FURHAT_AUTH_KEY` env var for the startup default, and an
  auth-key field (password-masked) in the web UI's connection panel, per
  `/api/robot/connect`.

## [0.1.8] - 2026-08-10
### Added
- `FurhatDemoController`'s opendemo Q&A turn is now a continuous multi-question
  loop instead of one question per button press: keeps listening and
  answering until an exit phrase ("bye", "goodbye", "stop asking", etc.), two
  consecutive silences, or a 10-turn safety cap, then says a goodbye line.
  A single silence gets one spoken nudge and the loop continues.

## [0.1.7] - 2026-08-06
### Added
- Web UI: a "Robot connection" panel to enter the robot's IP and see live
  connection status (●Connected / ●Not connected, with the error shown),
  polling `/api/robot/status` every 10s.
- `POST /api/robot/connect` (body: `{"host": "..."}`) and `GET
  /api/robot/status` — the app's active `DemoController` is now mutable
  runtime state (`furhat_demos.webui.robot_connection.RobotConnection`)
  instead of fixed once at startup; `/api/select` always uses whichever
  controller is currently connected.
- `FURHAT_HOST` still works exactly as before as the startup default; this
  adds a runtime override on top, it doesn't replace it.

### Fixed
- The connectivity probe now enforces its own hard wall-clock deadline
  (5s), independent of the Furhat Remote API client's internal retry
  behavior. Real-world testing found `_request_timeout` alone doesn't
  bound total latency — the client retries a failed connection attempt
  ~3 times internally, so an unreachable-but-not-actively-refusing host
  could hang ~10s+ rather than the intended few seconds. See ADR-006.

## [0.1.6] - 2026-08-06
### Added
- `FurhatDemoController` now runs a live, single-turn Q&A round on the
  opendemo option: after its intro (now spoken with `blocking=True` so
  `listen()` doesn't pick up the tail of its own speech), it listens once
  for a question, answers via that persona's `QAEngine`, and speaks the
  answer. `SILENCE`/`INTERRUPTED`/`FAILED`/empty listen results get a
  graceful spoken fallback instead of a nonsense LLM call.
- `furhat_demos.opendemo.personas`: builds a persona-specific `QAEngine` —
  `guide` uses the general Handbook content; `wafa-johal` uses Handbook
  content plus a dedicated bio doc (the Handbook doesn't cover individual
  researchers), with her own first-person system prompt.
- `build_controller()` now wires in a real `OpenAIChatClient` when
  `OPENAI_API_KEY` is set; left unset, the opendemo Q&A turn is skipped
  (intro-only), matching prior behavior.
- The web UI's `/api/select` now catches any `DemoController` failure
  (e.g. the robot being unreachable) and returns a clean `503` instead of
  an unhandled-exception traceback.

### Known limitation
- Still single-turn — one question per button press, not an ongoing
  conversation. Tracked in `BACKLOG.md`.

## [0.1.5] - 2026-08-06
### Added
- `furhat_demos.opendemo.handbook`: fetch + parse University of Melbourne
  Handbook search results and subject/course detail pages
  (handbook.unimelb.edu.au) into clean text, via an injectable HTTP client.
- `scripts/ingest_handbook.py`: offline CLI that caches a curated set of
  Handbook pages as markdown into `src/furhat_demos/opendemo/data/` — the
  live demo reads only this cache, never the Handbook site directly.

### Changed
- Replaced the 3 hand-written placeholder Open Day docs with real,
  ingested Handbook content (Diploma in Computing, Foundations of
  Computing, Algorithms and Data Structures) as a first representative set.

### Known limitations
- Ingested chunks are coarse (whole-page, not split by section) and carry
  some breadcrumb/nav boilerplate — see `BACKLOG.md`.

## [0.1.4] - 2026-08-05
### Added
- `QAEngine` (`furhat_demos.opendemo.qa`): a retrieval-grounded Q&A core for
  Demo 1. Retrieves relevant chunks from placeholder Open Day/curriculum docs
  by word-overlap scoring, then answers via an injected `LLMClient` — or
  returns a fixed "I don't know" style response without calling the LLM at
  all when no relevant chunk is found.
- `OpenAIChatClient`, a real `LLMClient` implementation using the `openai`
  package (needs `OPENAI_API_KEY`); tests use a fake client, no network calls.
- Placeholder Open Day/curriculum content under `src/furhat_demos/opendemo/data/`.

### Known limitation
- Retrieval is plain word-overlap (no stemming/embeddings), so it's brittle
  to vocabulary mismatch between the question and the source text — see
  ADR-003 and `ASSUMPTIONS.md` A-006.

## [0.1.3] - 2026-08-05
### Added
- `FurhatDemoController` now ensures an English voice is selected on the
  connected robot (via `get_voices`/`set_voice`) before it speaks, since
  language is tied to voice choice rather than a separate `say()` parameter.
  Selection happens once per controller instance; if no English voice is
  found or the lookup fails, it logs a warning and speaks anyway rather than
  blocking the demo.

## [0.1.2] - 2026-08-05
### Added
- `FurhatDemoController`, a real `DemoController` that speaks a placeholder
  intro via Furhat's Remote API (`furhat_remote_api`) for each demo/option.
- `FURHAT_HOST` environment variable to select it; unset, the app keeps
  defaulting to `LoggingDemoController` for local UI development.

## [0.1.1] - 2026-08-05
### Added
- Web UI (FastAPI + static page) for picking a demo and an option, backed by a
  pluggable `DemoController` interface (stub `LoggingDemoController` for now).

### Changed
- Dropped the QR-code camera trigger in favor of the web UI: Furhat's Remote
  API has no camera/vision access at all, so QR reading would have required
  a separate on-robot Kotlin bridge skill. See ADR-001.

## [0.1.0] - 2026-08-05
### Added
- Initial project scaffold.
