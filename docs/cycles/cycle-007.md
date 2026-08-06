# Cycle 007 — Robot IP entry + live connection status in the web UI

- **Date finalized:** 2026-08-06
- **Branch:** `feat/robot-connection-ui`
- **Version:** `0.1.6` → `0.1.7` (bump: patch)

## Plan (as approved)
- **Scope:** `RobotConnection` (mutable app state holding the active `DemoController` + status), `POST /api/robot/connect` / `GET /api/robot/status` endpoints, a "Robot connection" panel in the web UI (IP input, Connect button, live status indicator polling every 10s). `FURHAT_HOST` still works as the startup default; this adds a runtime override.
- **Files touched:** `src/furhat_demos/webui/robot_connection.py` (new), `src/furhat_demos/webui/app.py` (new endpoints, mutable connection state, `/api/select` reads current controller), `src/furhat_demos/config.py` (extracted `build_llm_client()` for reuse), `src/furhat_demos/control.py` (`get_voices` protocol now accepts `**kwargs` for the timeout), `src/furhat_demos/webui/static/index.html` (connection panel UI), plus tests across all of these.
- **Tests added:** `test_robot_connection.py` (connect success/failure, default state, probe/factory defaults, hard-deadline enforcement), extended `test_app.py` (status/connect endpoints, `/api/select` using the currently-connected controller, auto-connect at boot when `FURHAT_HOST` set).

## Assumptions added
- **A-009** (new): the 5s hard connect deadline is a judgment call, not validated against a genuinely slow-but-real network — only against a fast local network and a deliberately unreachable test IP.
- **A-002** (existing) already flagged the "No route to host" observation from cycle-006; this cycle is the direct follow-up fixing the underlying latency-bounding gap it exposed.

## Decisions made
- **ADR-006** — runtime robot IP entry (mutable `DemoController` state) + a hard, self-enforced connect deadline independent of the Furhat client's internal retry behavior.

## Test & coverage results
- Tests: 60/60 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- **Real bug caught and fixed mid-cycle, not just planned work**: manually testing the connection panel in an actual browser against a deliberately unreachable IP (`10.255.255.1`) revealed the probe hung far longer than the intended 3s timeout — confirmed by direct testing (`FurhatRemoteAPI(...).get_voices(_request_timeout=3)` took ~9-10s+ against that host). Root cause: urllib3's default retry behavior (3 attempts) multiplies the per-call timeout, and nothing in `FurhatRemoteAPI`'s public API exposes a way to disable it. Fixed by enforcing an independent hard deadline via a thread pool + `Future.result(timeout=...)`, verified afterward: the same unreachable IP now returns in ~5s with a clear "Timed out after 5s..." message, both via `curl` and in an actual browser session.
- This is exactly the kind of thing that could easily have shipped untested and only been discovered by the user hitting a hung "Connecting…" spinner during a real demo — caught here instead because the plan included manually clicking through the feature in a browser rather than stopping at green unit tests.
- Manually verified end-to-end in the browser: initial "Not connected" state, IP entry + Connect, live status update, and the timeout error message rendering correctly in the UI.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
