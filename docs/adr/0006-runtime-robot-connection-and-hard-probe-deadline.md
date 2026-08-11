# ADR-006: Runtime robot IP entry + a hard, self-enforced connect deadline

- **Status:** accepted
- **Date:** 2026-08-06
- **Cycle:** cycle-007

## Context

Until this cycle, `DemoController` was fixed once at app startup from the `FURHAT_HOST` env var — changing the robot's IP meant restarting the app. The user asked for a way to enter the IP from the web UI and see connection status live.

While building the reachability probe for this, manual testing surfaced a real problem: calling `remote_api.get_voices(_request_timeout=3)` against an unreachable-but-not-actively-refusing IP (`10.255.255.1`) took far longer than 3 seconds to raise — confirmed by direct testing to be ~9-10s+. Reading the generated client's source (`swagger_client.rest.RESTClientObject.request`) showed `_request_timeout` is passed straight through to `urllib3.PoolManager.request(..., timeout=...)`, but that call has no explicit `retries=` argument, so urllib3's own default retry behavior (observed: 3 total attempts) multiplies the effective wait — and there's no parameter exposed anywhere in `FurhatRemoteAPI`'s public surface to disable or reconfigure that.

## Decision

1. **The active `DemoController` becomes mutable runtime state** (`RobotConnection`), swappable via `POST /api/robot/connect`, with status exposed via `GET /api/robot/status`. `FURHAT_HOST` still sets the startup default; this adds a runtime override on top rather than replacing it.
2. **`RobotConnection.connect()` enforces its own hard wall-clock deadline** (`PROBE_DEADLINE_SECONDS = 5.0`) around the probe call, using a `ThreadPoolExecutor` + `Future.result(timeout=...)`, independent of whatever retry behavior the underlying HTTP client does internally. A probe that exceeds the deadline is treated as "not connected" and its thread is abandoned (not cancelled — network I/O can't be interrupted once blocked — just left to finish in the background and discarded).

## Alternatives considered

- **Reconfigure urllib3 retries at the client level** — rejected: would require reaching into `FurhatRemoteAPI`'s private internals (`api_client.rest_client.pool_manager`) since no public parameter exposes this; fragile against library updates.
- **Just trust `_request_timeout`** — the original (implicit) approach; disproven by direct testing during this cycle, see Context.
- **Block `connect()` until the probe naturally finishes, however long that takes** — rejected: defeats the entire purpose of showing live connection status in a UI a person is looking at.

## Consequences

- Connection attempts are now bounded to ~5s regardless of network conditions or the underlying client's retry behavior — verified by direct testing (both the original ~10s hang and the fixed ~5s bound).
- The abandoned-thread approach means a slow probe's thread keeps running in the background after `connect()` returns; harmless for this app's usage pattern (occasional manual connects, small thread pool) but not appropriate if this became a high-frequency operation.
- 5 seconds is a judgment call, not derived from any real slow-network measurement — see `ASSUMPTIONS.md` A-009. Adjustable via `RobotConnection(probe_deadline_seconds=...)` if real-world testing shows it's too aggressive.
- No authentication on the new endpoints — acceptable for a local/LAN kiosk tool, not solved here (tracked in `BACKLOG.md`).
