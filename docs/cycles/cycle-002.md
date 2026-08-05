# Cycle 002 — Real Furhat-backed DemoController

- **Date finalized:** 2026-08-05
- **Branch:** `feat/furhat-remote-controller`
- **Version:** `0.1.1` → `0.1.2` (bump: patch)

## Plan (as approved)
- **Scope:** add `FurhatDemoController`, wrapping `furhat_remote_api.FurhatRemoteAPI`, mapping each `(demo_id, option_id)` to a placeholder spoken intro via `.say()`. Select it via a `FURHAT_HOST` env var, defaulting to the existing `LoggingDemoController` when unset. Wire selection into the FastAPI app's default controller.
- **Files touched:** `src/furhat_demos/control.py` (added `FurhatDemoController`, `RemoteApi` protocol), `src/furhat_demos/config.py` (new — `build_controller()`), `src/furhat_demos/webui/app.py` (default controller now `build_controller()`), `pyproject.toml` (added `furhat-remote-api` dependency).
- **Tests added:** `tests/test_control.py` (extended — `FurhatDemoController` against a fake remote-API object: known intros, distinct texts per combo, fallback for unknown combos), `tests/test_config.py` (new — controller selection for unset/blank/set `FURHAT_HOST`, via `monkeypatch`).

Deviation from the original plan (discovered during implementation, not a scope change): dropped the planned `FURHAT_PORT` env var — `FurhatRemoteAPI.__init__` only accepts a `host` and always targets port `54321` internally, so a configurable port isn't meaningful. Recorded in ADR-002.

## Assumptions added
- **A-004** (new): `FurhatDemoController`'s real Furhat connection is unverified against a live instance in this environment — tested only via a mocked `RemoteApi`. Manual verification against Furhat Virtual, then the physical robot, is the next step.
- **A-002** (existing) remains relevant and unchanged — physical robot / Furhat Virtual availability for control-API testing.

## Decisions made
- **ADR-002** — Select `DemoController` via `FURHAT_HOST` env var, default to logging when unset.

## Test & coverage results
- Tests: 14/14 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Confirmed `FurhatRemoteAPI(host)` does not make a network call at construction time (just builds a `swagger_client` config) — safe to construct/select in `build_controller()` without side effects even if the host is unreachable; the actual network call only happens on `.say(...)`.
- Manually ran the app end-to-end with `FURHAT_HOST` unset (default `LoggingDemoController` path) via `curl` — `POST /api/select` still returns 200 as before. The `FurhatDemoController` path (`FURHAT_HOST` set) has no live robot/Virtual to check against here — flagged as A-004 and added to the backlog for the user to verify.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
