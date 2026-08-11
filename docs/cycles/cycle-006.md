# Cycle 006 — Live opendemo Q&A: personas, listen/answer/say, clean connectivity errors

- **Date finalized:** 2026-08-06
- **Branch:** `feat/opendemo-live-qa`
- **Version:** `0.1.5` → `0.1.6` (bump: patch)

## Plan (as approved)
- **Scope:** persona-specific `QAEngine` construction (`guide` vs `wafa-johal`, the latter needing a new bio doc since the Handbook doesn't cover individual researchers); `FurhatDemoController.start_demo` runs a single-turn listen→answer→say round for the opendemo demo when an `LLMClient` is configured; `build_controller()` wires in `OpenAIChatClient` when `OPENAI_API_KEY` is set.
- **Added mid-plan** (motivated by the user's real robot test, see Notes): the web UI's `/api/select` now catches `DemoController` failures and returns a `503` instead of an unhandled-exception traceback.
- **Files touched:** `src/furhat_demos/opendemo/{personas.py,data/personas/wafa-johal.md}`, `src/furhat_demos/opendemo/qa.py` (added `system_prompt` param), `src/furhat_demos/control.py` (QA turn, `ListenResult`/`listen` on `RemoteApi`), `src/furhat_demos/config.py` (wire `OpenAIChatClient`), `src/furhat_demos/webui/app.py` (503 handling), plus tests across all of these.
- **Tests added:** persona-specific system prompt/content selection (`test_personas.py`), QA-turn control flow fully mocked — triggered only for opendemo+llm_client, skipped otherwise, graceful fallback on `SILENCE`/`None` listen results, intro blocking behavior (`test_control.py`), controller/LLM-client wiring by env var (`test_config.py`), 503 on controller exception (`test_app.py`).

## Assumptions added
- **A-008** (new): the real `listen()` path (recognition behavior, and whether blocking the intro actually prevents self-listening) is unverified — only mocked in tests.
- **A-002** updated with a note: user observed a real "No route to host" connectivity error testing against the physical robot mid-cycle — motivated the 503 addition.

## Decisions made
- **ADR-005** — single-turn Q&A per button press; fail cleanly (503, logged) rather than silently on robot connectivity errors, unlike the deliberately-silent voice-selection fallback from cycle-003.

## Test & coverage results
- Tests: 49/49 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Mid-cycle, the user reported a real `OSError: [Errno 65] No route to host` testing `FurhatDemoController` against the physical robot at a hotspot-style IP (`172.20.10.10`) — diagnosed as a network/routing issue on their end (laptop likely not on the same network as the robot at that moment), not a code bug. It did expose a real gap (unhandled exception → raw traceback), fixed via the 503 addition described above; folded into this cycle since it touches the same code area rather than opened as a separate cycle.
- Deliberately did **not** make `FurhatDemoController` swallow connectivity errors the way it does for voice-selection — see ADR-005 for the reasoning (a silent no-response is worse than a visible failure for an unattended demo).
- Manually confirmed the app still boots and the existing no-robot/no-API-key path (`LoggingDemoController`, or `FurhatDemoController` with `llm_client=None`) is unaffected.
- The live `listen()`/QA-turn path itself is untested against real hardware in this environment (no live Furhat reachable here) — flagged as A-008 and the top of `BACKLOG.md`'s "Next" list for the user to verify.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
