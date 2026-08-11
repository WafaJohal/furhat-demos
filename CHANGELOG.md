# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
