# ADR-005: Single-turn Q&A per button press; fail cleanly (not silently) on robot connectivity errors

- **Status:** accepted
- **Date:** 2026-08-06
- **Cycle:** cycle-006

## Context

Wiring `QAEngine` into `FurhatDemoController` requires deciding how many questions a visitor gets per button press, and how the system should behave when the robot is unreachable — the latter became concrete when the user hit a real `OSError: [Errno 65] No route to host` testing against a physical robot, which crashed the web request with a raw unhandled-exception traceback.

## Decision

1. **Single-turn Q&A**: pressing an opendemo option speaks an intro, listens once, answers once. It is not a continuous conversation loop. The intro is spoken with `blocking=True` specifically when a QA turn will follow, so `listen()` doesn't start while the robot is still mid-sentence (and potentially hear its own voice as the "question").
2. **Fail cleanly, not silently, on connectivity errors**: unlike the English-voice selection (cycle-003), which deliberately swallows errors and continues (voice choice is a nice-to-have), a failure to reach the robot for `say()`/`listen()` is a real failure the caller should know about. `FurhatDemoController` does **not** catch these — they propagate. The web UI's `/api/select` endpoint catches them at that boundary and returns a `503` with a clear message, instead of leaking a raw traceback to the client.

## Alternatives considered

- **Continuous listen loop** (keep asking until some exit phrase/timeout) — more natural for a real demo, but bigger scope and harder to test/reason about; deferred to `BACKLOG.md`.
- **Swallow connectivity errors in the controller too** (log and return silently, like the voice-selection fallback) — rejected: unlike voice choice, a visitor who presses a button and gets no response at all with no error surfaced anywhere is a much worse failure mode, especially during an unattended Open Day demo. Failing loudly (503, logged) at least gives a chance to notice and fix a disconnected robot quickly.

## Consequences

- A visitor must press the option again to ask a follow-up question — an accepted limitation for this cycle, not a bug.
- Robot connectivity issues now surface as a clean `503` with a human-readable message rather than a stack trace, but still require someone watching for them (no alerting/retry built) — acceptable for a staffed demo, revisit if this needs to run unattended.
- The real `listen()` path (recognition quality, timeout behavior, and whether blocking the intro actually prevents self-listening) is unverified in this environment — see `ASSUMPTIONS.md` A-008.
