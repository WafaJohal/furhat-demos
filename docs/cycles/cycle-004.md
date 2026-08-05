# Cycle 004 — Q&A core for Demo 1 (text in/out, no voice yet)

- **Date finalized:** 2026-08-05
- **Branch:** `feat/opendemo-qa-core`
- **Version:** `0.1.3` → `0.1.4` (bump: patch)

## Plan (as approved)
- **Scope:** `QAEngine`, a retrieval-grounded answering core: loads placeholder Open Day/curriculum docs, chunks them, retrieves relevant chunks by word-overlap scoring, and answers via an injected `LLMClient` — or returns a fixed "I don't know" response without calling the LLM at all when nothing relevant is found. Decoupled from Furhat/web UI (that wiring is next).
- **Files touched:** `src/furhat_demos/opendemo/{__init__.py,qa.py,llm_client.py,data/*.md}`, `tests/opendemo/{test_qa.py,test_llm_client.py}`, `pyproject.toml` (added `openai`).
- **Tests added:** retrieval/answer behavior against a fake `LLMClient` (grounded answer, "I don't know" fallback with zero LLM calls, empty/punctuation-only question, ranking with `top_k`, real placeholder-file loading strips HTML comments), and `OpenAIChatClient` against a mocked `openai.OpenAI` (no real network calls).

Deviation from the original plan (implementation detail, not scope change): placeholder docs live under `src/furhat_demos/opendemo/data/` (co-located with the module, matching the `webui/static/` pattern) rather than a top-level `data/` directory.

## Assumptions added
- **A-005** (existing) marked `validated` — user confirmed the English-voice selection works on a connected robot.
- **A-006** (new): plain word-overlap retrieval is brittle to vocabulary mismatch — marked `invalidated` for the general case. Demonstrated live during manual smoke-testing (see Notes).

## Decisions made
- **ADR-003** — word-overlap retrieval (not embeddings) for this first cycle, with the known limitation and follow-up recorded.

## Test & coverage results
- Tests: 25/25 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Also fixed a merge gap discovered before this cycle started: PR #2's merge only included the cycle-002 commit, silently dropping the already-tested cycle-003 (English voice) commit from `main`. Recovered via a separate small PR (#3, `chore/restore-cycle-003`) cherry-picking it back in, unrelated to this cycle's actual scope but done first so this branch built on the correct base.
- Manually ran `QAEngine` against the real placeholder data (not just synthetic test fixtures) with an echo-style fake LLM client, across a few realistic Open Day questions. Caught a real retrieval miss: "What courses do you offer?" hit the "I don't know" fallback because `courses.md` never used the literal word "courses". Fixed the placeholder doc's wording as a cheap mitigation; the structural limitation (word-overlap retrieval generally) is tracked via ADR-003/A-006, not fixed in this cycle.
- `OpenAIChatClient` is implemented and unit-tested but not exercised against a live OpenAI account in this environment — no `OPENAI_API_KEY` available here. Real end-to-end answering (LLM call included) still needs manual verification once wired into an actual demo flow.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
