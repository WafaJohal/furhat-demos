# Cycle 003 — Ensure English voice before speaking

- **Date finalized:** 2026-08-05
- **Branch:** `feat/furhat-remote-controller` (same branch/PR as cycle-002 — still unmerged when this work started)
- **Version:** `0.1.2` → `0.1.3` (bump: patch)

## Plan (as approved)
- **Scope:** `FurhatDemoController` ensures an English voice is selected (via `get_voices()`/`set_voice()`) before its first spoken line, since language is tied to voice choice rather than a `say()` parameter. Done once per controller instance (cached), defensively (logs a warning and still speaks if no English voice is found or the lookup fails).
- **Files touched:** `src/furhat_demos/control.py` (`_ensure_english_voice`, extended `RemoteApi`/new `VoiceLike` protocol), `tests/test_control.py` (extended `FakeRemoteApi`/new `FakeVoice` fakes, 4 new tests).
- **Tests added:** matching English voice gets selected; only queried/set once across multiple `start_demo()` calls; no-English-voice case warns and still speaks; voice-lookup exception warns and still speaks.

Context: this cycle started only after the user manually confirmed cycle-002's `FurhatDemoController` actually connects to a real robot and speaks when a web UI option is pressed — validating `ASSUMPTIONS.md` A-004.

## Assumptions added
- **A-004** updated to `validated` (real Furhat connection + speech confirmed by the user).
- **A-005** (new): the English-voice selection itself is unverified against a live robot — implemented defensively for exactly this reason. Needs manual confirmation.

## Decisions made
- None requiring a new ADR — small, direct extension of the controller added in cycle-002 (already covered by ADR-002's scope).

## Test & coverage results
- Tests: 18/18 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Confirmed via `swagger_client.models.voice.Voice` that voices have `name` + `language` fields; matched on `language.lower().startswith("en")` to tolerate formats like `en-US`, `en-GB`, or a bare `"English"`.
- Deliberately fail-soft: a voice-selection error must not block the "press button, robot talks" flow during a live demo.

## PR
- Link / reference: https://github.com/WafaJohal/furhat-demos/pull/2 (same PR as cycle-002; pushing this as an additional commit)
- Merge status: pending user
