# Cycle 001 — Web UI for demo & option selection

- **Date finalized:** 2026-08-05
- **Branch:** `feat/webui-demo-selector`
- **Version:** `0.1.0` → `0.1.1` (bump: patch)

## Plan (as approved)
Originally planned as a QR-code camera-reading spike (camera feed → external decoder). Before coding began, investigation showed Furhat's Remote API has no camera/vision access at all (confirmed by inspecting `furhat_remote_api`'s public methods), so QR reading would need a separate on-robot Kotlin bridge skill. The user chose to drop QR entirely in favor of a web UI. Revised, approved plan:

- **Scope:** small FastAPI backend + static HTML/JS page listing the two demos and their options; selections call a pluggable `DemoController` interface; ships with a `LoggingDemoController` stub (no real robot integration yet).
- **Files touched:** `src/furhat_demos/control.py`, `src/furhat_demos/webui/{app.py,demos.py,static/index.html,__init__.py}`, `tests/test_control.py`, `tests/webui/test_app.py`, `pyproject.toml` (added `fastapi`, `uvicorn`, `httpx`).
- **Tests added:** `tests/test_control.py` (stub controller logging), `tests/webui/test_app.py` (demo listing shape, valid/invalid selection via `TestClient`, default-controller wiring, index page served).

## Assumptions added
- A-001 marked **invalidated** (superseded by this cycle's decision — QR dropped before being tested; also confirmed moot since Remote API has no camera access regardless).
- A-002 updated: no longer tied to camera-feed work specifically; still relevant for future Remote/Realtime API robot control.

## Decisions made
- **ADR-001** — Web UI for demo/option selection, instead of a QR-code camera trigger.

## Test & coverage results
- Tests: 8/8 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Manually ran the web UI (`uvicorn`) and verified the full flow in a real browser: demo list renders, clicking an option posts to `/api/select` and shows "Started: opendemo / wafa-johal", confirmed via network request inspection.
- Caught and fixed a real contrast bug during that manual check: the page had no explicit colors, so it inherited the browser's dark color-scheme for the background while text stayed black — nearly unreadable. Fixed by setting `color-scheme: light` and explicit background/text colors, since this is meant to run predictably on a kiosk/tablet regardless of the browser's theme.
- `DemoController` is still a stub — wiring it to a real Furhat connection (Remote/Realtime API), testable against Furhat Virtual first, is the next backlog item.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
