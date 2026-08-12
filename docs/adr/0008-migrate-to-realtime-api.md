# ADR-008: Migrate from the Remote API to the Realtime API

- **Status:** accepted
- **Date:** 2026-08-12
- **Cycle:** cycle-009

## Context

Since cycle-002, this project has driven Furhat via `furhat_remote_api.FurhatRemoteAPI` — a REST-style HTTP client hitting port `54321`. Cycles 006/007 built increasingly careful error handling around that connection (voice selection, connectivity timeouts, a runtime IP-entry UI), all working correctly in their own terms.

Real-robot and Furhat Virtual testing (2026-08-06 through 2026-08-12) kept failing with "Connection refused" or "No route to host" against that port, across multiple diagnoses (network routing, the Remote API Skill not running). The actual cause, surfaced when the user shared Furhat's Realtime API documentation: **Furhat has two separate control APIs**, and the robot/Virtual in use only has the newer **Realtime API** enabled — a WebSocket protocol on port `9000`, disabled by default, with its own security/auth model (`request.auth` handshake with an optional key configured via the robot's web interface). Every "Connection refused" was port `54321` correctly reporting nothing listens there, because the Remote API was never the thing enabled on this setup at all.

Checked the Realtime API's Python client (`furhat_realtime_api`, confirmed via official examples at `FurhatRobotics/realtime-api-examples`): `FurhatClient(host, auth_key=None)` is synchronous (runs its own background event loop), so it drops into this project's existing sync architecture with no rewrite of the app itself needed.

## Decision

Replace `furhat_remote_api` with `furhat_realtime_api.FurhatClient` as the sole transport. Specifically:
- `FurhatDemoController` takes a new `FurhatRealtimeClient` protocol (`connect`, `disconnect`, `request_speak_text`, `request_listen_start`, `request_voice_config`, `request_attend_user`) instead of the old `RemoteApi` protocol.
- Voice selection collapses from "list voices, filter for English, set by name" to one `request_voice_config(language="en-US")` call — the new API supports filtering natively.
- `request_attend_user()` added on every `start_demo()` (the official example calls this; we didn't have an equivalent before).
- `say`/`blocking` maps to `request_speak_text(text, wait=blocking)`. `listen` maps to `request_listen_start()`, which returns a plain string (`""` on no speech) — simpler than the old `SILENCE`/`INTERRUPTED`/`FAILED` string sentinels.
- `RobotConnection.connect()`'s hard deadline (ADR-006) carries over unchanged in spirit: `client.connect()` itself now does the work the old separate "construct + probe" split did (it performs the WebSocket handshake *and* the auth exchange), so there's no separate probe step anymore — just `connect()` wrapped in the same thread-pool deadline, since nothing guarantees the underlying `websockets.connect()` is bounded either.
- Added `auth_key` support end-to-end: `FURHAT_AUTH_KEY` env var, `RobotConnection.connect(host, auth_key)`, `/api/robot/connect`'s request body, and a password-masked field in the web UI panel.
- Removed now-wrong code: the `furhat-remote-api` dependency, `VoiceLike`/`ListenResult` protocols, `config.build_controller()` (was already unused by the app — see cycle-009 development notes).

## Alternatives considered

- **Keep the Remote API, just fix connectivity** — not viable: the port the Remote API needs was never going to be listening on this setup regardless of network/firewall fixes, since only the Realtime API is enabled.
- **Wrap `FurhatClient` behind the old `RemoteApi`-shaped protocol** (adapter, minimal diff) — considered for speed, but rejected in favor of using the new client's native methods directly: the Realtime API's shape is genuinely better suited (native language-filtered voice config, `wait=` built into speak, `request_attend_user`), and forcing it through the old shape would have thrown away those wins for no real benefit once a rewrite was happening anyway.

## Consequences

- Confirmed working by the user against a real connection post-migration ("it works now") — resolves the multi-week connectivity investigation across cycles 006-009.
- `config.build_controller()`'s removal is a breaking change to this project's own internal surface (pre-1.0, so this bumps MINOR per `references/semver.md`, not PATCH) — no external consumers, but worth noting since it was a public function.
- Discovered a minor, environment-specific robustness gap during manual testing: `connect()` succeeding (WS + auth handshake) isn't airtight proof of talking to a real Furhat — see `ASSUMPTIONS.md` A-012. Not fixed this cycle; tracked as a hardening idea.
- The real `listen()`/Q&A-loop path is now presumed working (the user's next feedback was about persona/content choices, not loop mechanics) but not explicitly, granularly confirmed — see A-008's update.
