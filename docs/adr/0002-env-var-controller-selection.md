# ADR-002: Select DemoController via FURHAT_HOST env var, default to logging

- **Status:** accepted
- **Date:** 2026-08-05
- **Cycle:** cycle-002

## Context

The web UI (cycle-001) always used a stub `LoggingDemoController`. This cycle adds `FurhatDemoController`, a real implementation that drives a Furhat instance (virtual or physical) via `furhat_remote_api.FurhatRemoteAPI`. The app needs a way to pick between them without a code change, since local UI development (no robot reachable) and actual demo/testing runs (robot reachable) happen on the same codebase.

`FurhatRemoteAPI(host)` takes only a `host` string and always targets port `54321` internally (confirmed by reading its `__init__`) — there is no separate configurable port.

## Decision

We will select the controller via a single `FURHAT_HOST` environment variable, read by `furhat_demos.config.build_controller()`:
- Unset or blank → `LoggingDemoController` (safe default; matches all prior behavior).
- Set (e.g. `localhost` for Furhat Virtual, or the robot's IP) → `FurhatDemoController(FurhatRemoteAPI(host))`.

`create_app()` keeps its existing `controller` parameter for direct injection (used by tests), and only calls `build_controller()` when no controller is passed in.

## Alternatives considered

- **Config file** — more ceremony than needed for a single value at this stage; env var matches how the host would vary between a developer's laptop, Furhat Virtual, and the physical robot's network.
- **Always require `FURHAT_HOST`** (no logging fallback) — rejected: would break local UI iteration for anyone without a robot/Virtual instance reachable, which is the common case during Demo 1/2 development.

## Consequences

- Local development stays zero-config (no robot needed) — only set `FURHAT_HOST` to actually drive a robot.
- No port configurability is needed or exposed, since the dependency itself doesn't support it.
- `FurhatDemoController` has not been exercised against a live Furhat/Furhat Virtual instance in this environment — see `ASSUMPTIONS.md` A-004. Manual verification is on the user.
