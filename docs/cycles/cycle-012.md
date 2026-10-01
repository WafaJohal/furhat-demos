# Cycle 012 — Remove the Open Day Q&A demo; simplify to a single-demo UI

- **Date finalized:** 2026-10-01
- **Branch:** `chore/remove-opendemo-single-demo-ui`
- **Version:** `0.3.2` → `0.4.0` (bump: minor — breaking removal, pre-1.0 convention established by cycle-003/ADR-era 0.3.0 bump)

## Plan (as approved)
- **Scope:** delete the Open Day Q&A demo (`furhat_demos.opendemo`) entirely — QA engine, personas, LLM client, Handbook scraper/ingestion script, admin PDF-upload page/routes — and the now-dead QA-loop/LLM-client wiring in `control.py`/`config.py`/`robot_connection.py`. Replace the generic demo-picker web UI with a single hardcoded "Start FaceVis" button/endpoint, since FaceVis is the only demo left. Drop now-unused dependencies.
- **Files touched:**
  - Deleted: `src/furhat_demos/opendemo/` (package + data), `tests/opendemo/` (tests + fixtures), `scripts/` (only held `ingest_handbook.py`), `src/furhat_demos/webui/static/admin.html`, `src/furhat_demos/webui/demos.py`, `tests/test_config.py`.
  - Edited: `src/furhat_demos/webui/app.py` (drop admin/select/demos routes, add `POST /api/facevis/start`), `src/furhat_demos/webui/static/index.html` (single-button page), `src/furhat_demos/control.py` (drop QA loop/exit-phrase/LLM-client code), `src/furhat_demos/config.py` (drop `OPENAI_API_KEY_ENV_VAR`/`build_llm_client`), `src/furhat_demos/webui/robot_connection.py` (drop `llm_client=` kwarg), `tests/webui/test_app.py`, `tests/test_control.py`, `pyproject.toml` (drop `openai`/`pypdf`/`beautifulsoup4`/`python-multipart`).
- **Tests:** removed all opendemo/admin/QA-loop tests; added `test_start_facevis_calls_controller` and `test_start_facevis_returns_503_when_controller_raises` for the new endpoint; repointed remaining `control.py` intro/voice/attend tests at `("facevis", "air-quality")`.

## Assumptions added
- None — this cycle only removes code and narrows scope; no new unverified claims were introduced. (Previously open opendemo-only assumptions, e.g. around Handbook HTML stability and the word-overlap retrieval heuristic, are now moot since that code no longer exists — left as historical record in `ASSUMPTIONS.md` rather than deleted, consistent with how ADRs are handled.)

## Decisions made
- **ADR-012** — remove `opendemo` in full; collapse the demo-selection abstraction (`/api/demos`, `/api/select`, `webui/demos.py`) to a single hardcoded `/api/facevis/start` endpoint now that there's only one demo; leave existing opendemo-only ADRs/cycle docs in place as historical record rather than rewriting them.

## Test & coverage results
- Tests: 73/73 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Verified the full flow live in the Browser pane against a local `uvicorn` server (`LoggingDemoController`, no robot/WAQI token): the simplified index page shows only the robot-connection panel and a "Start FaceVis" button (no demo list, no admin link); clicking it calls `POST /api/facevis/start` (200, logged) and opens `/facevis`, which correctly renders the Plotly world map with the "WAQI_API_TOKEN is not set" banner.
- `README.md`, `BACKLOG.md`, and `ASSUMPTIONS.md` updated to reflect the single-demo scope; `CHANGELOG.md` records the removal under `0.4.0`.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
