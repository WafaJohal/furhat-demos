# Cycle 008 — Continuous multi-question Q&A loop

- **Date finalized:** 2026-08-10
- **Branch:** `feat/opendemo-qa-loop`
- **Version:** `0.1.7` → `0.1.8` (bump: patch)

## Plan (as approved)
- **Scope:** replace `FurhatDemoController`'s single listen→answer→say round with a loop: keep listening and answering (via the persona's `QAEngine`, built once and reused across turns) until an exit phrase, two consecutive silences, or a 10-turn cap, then speak a goodbye line. A single silence gets one spoken nudge and the loop continues.
- **Files touched:** `src/furhat_demos/control.py` (`_run_qa_loop` replaces `_run_single_qa_turn`; new exit-phrase/turn-cap/goodbye constants), `tests/test_control.py` (rewritten `FakeRemoteApi.listen()` to serve a sequence of canned results instead of one static value; new tests for multi-question answering, single-silence nudge, double-silence exit, exit-phrase exit, max-turn cap).

## Assumptions added
- **A-010** (from the real-robot testing session, recorded before this cycle's code started): the "No route to host" issue from cycle-006/007 was diagnosed as the Furhat Remote API Skill not running on the robot (confirmed via `curl` getting "Connection refused", not a routing error) — not a code bug. Separately, checked that `furhat_remote_api`'s client has no built-in auth mechanism (`Configuration.auth_settings()` returns `{}`); an auth key, if genuinely required, isn't implemented yet — deferred to next week pending confirmation against a real robot with the skill actually running.
- **A-011** (new): the exit-phrase list is an untested heuristic against real speech-recognition output — needs manual verification alongside A-008 (the `listen()` path itself).

## Decisions made
- **ADR-007** — exit conditions for the loop (exit phrase before double-silence before turn cap), and why `"thanks"` was deliberately excluded from the exit-phrase list.

## Test & coverage results
- Tests: 62/62 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Manually ran the loop logic standalone (not just via pytest) with a scripted fake API and engine to eyeball the actual sequence of spoken lines end-to-end — matched the design exactly (intro blocking, answer blocking, goodbye non-blocking).
- Real-robot testing this session (before this cycle's code changes) resolved the "No route to host" mystery from cycle-006/007: it was the Remote API Skill not running on the robot, confirmed via a direct `curl` to the robot's port getting "Connection refused" rather than a routing error. The user separately raised a need for an authentication key on the connection — investigated but not implemented, since the underlying client has no auth mechanism at all and the actual requirement (if any) needs confirming against a real robot with the skill running, which the user is doing next week.
- User is testing the current connection/Q&A features against Furhat Virtual this week in parallel with this cycle's work.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
