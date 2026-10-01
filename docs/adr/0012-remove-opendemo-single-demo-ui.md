# ADR-012: Remove the Open Day Q&A demo; simplify to a single-demo UI

- **Status:** accepted
- **Date:** 2026-10-01
- **Cycle:** cycle-012

## Context

This project originally hosted two Furhat demos: Open Day Q&A
(`furhat_demos.opendemo`, a RAG-based Q&A engine over University of
Melbourne Handbook content and admin-uploaded PDFs) and FaceVis
(`furhat_demos.facevis`, driving the robot's face from live air-quality
data). The Open Day event this demo supported has passed, and the user
asked for the repository to be reduced to "a simple demo that only does the
air quality visualisation demo," removing any screens and code meant for
the Open Day Q&A.

## Decision

Remove `furhat_demos.opendemo` in full — `QAEngine`, personas, the
`LLMClient`/`OpenAIChatClient` protocol, the Handbook scraper and its
offline ingestion script, and the admin PDF-upload page/routes that fed the
engine's document pool (`/admin`, `/api/admin/documents`). Strip the
corresponding QA-turn loop, exit-phrase handling, and `llm_client` wiring
out of `FurhatDemoController`/`RobotConnection`/`config.py`.

With only one demo left, also drop the generic demo/option selection
abstraction (`furhat_demos.webui.demos`, `/api/demos`, `/api/select`) in
favor of a single hardcoded `POST /api/facevis/start` endpoint and a
one-button "Start FaceVis" page. The robot-connection panel (IP/auth-key
entry, live status) is demo-agnostic infrastructure and is unchanged.

Existing ADRs and cycle records that describe the removed feature (e.g.
ADR-0003–0005, 0007, 0009; cycles 004–006, 008, 010) are left in place as a
historical record of decisions made at the time, per standard ADR practice
— they are not rewritten or deleted even though the code they describe no
longer exists.

## Alternatives considered

- **Keep the demo-picker abstraction, just empty the list down to one
  entry** — rejected: with exactly one demo, the extra indirection
  (`/api/demos`, `/api/select`, the `Demo`/`DemoOption` registry) adds
  nothing a hardcoded button doesn't already provide, and the user asked for
  "simple."
- **Keep opendemo code but unwire it from the UI** — rejected: the user
  explicitly asked to remove the code and screens, not just hide them;
  retaining dead code would leave unused dependencies (`openai`, `pypdf`,
  `beautifulsoup4`) and an untested code path.
- **Delete the opendemo-only ADRs/cycle docs too** — rejected: ADRs record
  decisions as of the time they were made; rewriting history to pretend a
  removed feature was never built is not the convention this project
  follows elsewhere (see ADR-011's handling of the superseded Leaflet
  decision, ADR-010, which it still accurately describes).

## Consequences

- `pyproject.toml` loses `openai`, `pypdf`, `beautifulsoup4`, and
  `python-multipart` — none of FaceVis's code paths need them.
- `OPENAI_API_KEY` is no longer a recognized environment variable; only
  `FURHAT_HOST`, `FURHAT_AUTH_KEY`, and `WAQI_API_TOKEN` remain.
- The web UI's `/`, `/api/demos`, `/api/select`, `/admin`, and
  `/api/admin/documents` routes are removed; any external tooling or
  bookmarks pointing at them will break. `/facevis` and
  `/api/facevis/set_air_quality` are unchanged.
- Adding a second demo back in the future would need the selection
  abstraction reintroduced — acceptable, since it was straightforward to
  build the first time (cycle-001) and isn't needed for the project's
  current single-demo scope.
