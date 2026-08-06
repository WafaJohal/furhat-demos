# Cycle 005 — Handbook-backed content for QAEngine

- **Date finalized:** 2026-08-06
- **Branch:** `feat/handbook-ingestion`
- **Version:** `0.1.4` → `0.1.5` (bump: patch)

## Plan (as approved)
- **Scope:** `furhat_demos.opendemo.handbook` (injectable HTTP fetch + pure HTML parsers for search results and detail pages) and `scripts/ingest_handbook.py` (offline CLI caching a curated set of Handbook pages as markdown into `src/furhat_demos/opendemo/data/`, replacing the 3 hand-written placeholder docs). Parsing tested offline against real HTML fixtures — no live network calls in CI.
- **Files touched:** `src/furhat_demos/opendemo/handbook.py`, `scripts/ingest_handbook.py`, `tests/opendemo/{test_handbook.py,fixtures/*.html}`, `pyproject.toml` (added `beautifulsoup4`, promoted `httpx` to a main dependency), removed `src/furhat_demos/opendemo/data/{courses,teaching_approach,research}.md`.
- **Tests added:** search-results parsing (code/name/url extraction, malformed-result skip), detail-page parsing (title+body extraction, noise-line stripping, empty/missing-main-content edge cases), `search`/`fetch_detail_text` against a fake HTTP client, `RequestsHttpClient` against a mocked `httpx.Client`.

## Assumptions added
- **A-007** (new): Handbook site HTML structure could change and silently break parsing (`holding`); also notes the coarse-chunking/boilerplate content-quality issues found during manual smoke-testing.

## Decisions made
- **ADR-004** — cache Handbook content offline via an ingestion script; the live demo never fetches the Handbook site directly.

## Test & coverage results
- Tests: 36/36 passed (first pass landed at 99% coverage — 2 uncovered defensive branches; added 2 targeted edge-case tests to restore 100% before finalizing)
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Confirmed via direct `curl` (normal browser `User-Agent`, no JS) that the Handbook site returns full content with no bot-challenge, despite Incapsula being visible in network traces — this made the plain-HTTP-fetch design viable without needing a headless browser.
- Actually ran `scripts/ingest_handbook.py` against the live site and committed its real output (not synthetic placeholders) for 3 pages: Diploma in Computing (D-COMP), Foundations of Computing (COMP10001), Algorithms and Data Structures (COMP20003).
- Manually smoke-tested `QAEngine` against the real ingested content across several realistic questions — retrieval and the "I don't know" refusal both behaved correctly. Found two content-quality issues (not correctness bugs): chunks are whole-page rather than split by section, and each carries some breadcrumb/nav text. Both recorded in `ASSUMPTIONS.md` A-007 and `BACKLOG.md`, not fixed this cycle.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
