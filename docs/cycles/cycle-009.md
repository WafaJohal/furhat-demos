# Cycle 009 — Migrate to the Furhat Realtime API

- **Date finalized:** 2026-08-12
- **Branch:** `feat/realtime-api-migration`
- **Version:** `0.1.8` → `0.2.0` (bump: minor — breaking change to this project's own surface, pre-1.0 convention)

## Plan (as approved)
- **Scope:** replace `furhat_remote_api` (REST, port 54321) with `furhat_realtime_api.FurhatClient` (WebSocket, port 9000, built-in `auth_key`) — the API actually enabled on the robot/Virtual in use. Rewrite `FurhatDemoController` around the new `FurhatRealtimeClient` protocol; simplify voice selection to `request_voice_config(language="en-US")`; add `request_attend_user()`; `RobotConnection`/`config.py` swap in the new client with `auth_key` support; web UI gets an auth-key field. Remove now-wrong code (`furhat-remote-api` dependency, old protocols, unused `build_controller()`).
- **Files touched:** `src/furhat_demos/control.py` (full rewrite of the Furhat-facing side), `src/furhat_demos/config.py` (trimmed to just `build_llm_client()` + env var constants; `build_controller()` removed as dead code), `src/furhat_demos/webui/robot_connection.py` (client_factory + auth_key, `connect()` replaces the old construct+probe split), `src/furhat_demos/webui/app.py` (auth_key on `ConnectRequest` and the auto-connect-at-boot path), `src/furhat_demos/webui/static/index.html` (auth-key input), `pyproject.toml` (dependency swap), plus full test rewrites across `test_control.py`, `test_config.py`, `test_robot_connection.py`, `test_app.py`.
- **Tests:** all offline/mocked as before — fakes rewritten to match the new `FurhatRealtimeClient` protocol shape (`request_speak_text`, `request_voice_config`, `request_attend_user`, `request_listen_start`, `connect`) instead of the old one.

## Assumptions added
- **A-010** updated to `invalidated` — the real issue was the wrong API entirely, not a missing auth header or a skill-not-running problem. User confirmed "it works now" post-migration.
- **A-008** updated to `invalidated (superseded)` — was written about the old API's specific sentinel behavior, moot after the migration.
- **A-012** (new): `connect()` succeeding isn't airtight proof of talking to real Furhat — demonstrated via a real (environment-specific) false positive during manual testing, see Notes.

## Decisions made
- **ADR-008** — migrate to the Realtime API; use its native methods directly rather than wrapping it behind the old protocol shape.

## Test & coverage results
- Tests: 62/62 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- This cycle exists because the connectivity mystery spanning cycles 006-009 had the wrong root cause diagnosed each time (network routing, then "skill not running," then "needs an auth header") — the actual issue, surfaced only once the user shared Furhat's own Realtime API docs, was that the robot/Virtual never had the Remote API enabled at all, only the separate Realtime API. Confirmed via the official `furhat_realtime_api` package and its examples repo (`FurhatRobotics/realtime-api-examples`) before writing any code.
- **Real, unplanned finding during manual testing**: after implementing the migration, testing `connect()` against `127.0.0.1` in this dev sandbox reported "Connected" — but nothing Furhat-related was running here. Investigated: an unrelated Java process already listening on port 9000 (OS-registered service name "cslistener") responded to a raw `request.auth` WebSocket message with a well-formed, correct-looking `{"type":"response.auth","access":true,"scope":"localhost"}`, passing our check. Confirmed via a raw `websockets` script bypassing our code entirely — not a bug in this project, a coincidental artifact of this specific sandbox. Recorded as A-012 and a backlog hardening idea (a follow-up call after `connect()` would be a stronger liveness check) rather than fixed now, since it's not reproducible against real hardware and the real-world collision risk is low.
- User confirmed the migration works against their actual setup ("it works now") — resolving the multi-cycle connectivity investigation.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
