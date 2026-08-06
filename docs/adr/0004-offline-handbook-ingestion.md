# ADR-004: Cache Handbook content offline, don't fetch it live per question

- **Status:** accepted
- **Date:** 2026-08-06
- **Cycle:** cycle-005

## Context

The user pointed `QAEngine`'s content source at the University of Melbourne Handbook (handbook.unimelb.edu.au/search) — a real, comprehensive source (6,894 courses/subjects) with predictable URLs (`/search?query=...`, `/subjects/{code}`, `/courses/{code}`) and server-rendered HTML.

Investigation found: the site fronts requests with Incapsula (visible in network traces as an obfuscated bot-mitigation script), but a plain `curl` with a normal browser `User-Agent` got a clean `200` with full content — no challenge, no block. `robots.txt` is present but its disallow rules are commented out (effectively permissive). Individual detail pages carry `<meta name="robots" content="NOINDEX,NOFOLLOW">`, a signal to search engines not to index that specific page, not a statement about scripted access generally.

Two ways to use this as `QAEngine`'s content source: fetch live per visitor question, or fetch ahead of time and cache locally.

## Decision

We will fetch and cache Handbook content **ahead of time** via an offline script (`scripts/ingest_handbook.py`), writing plain markdown into `src/furhat_demos/opendemo/data/`. The live demo (`QAEngine`, and anything built on top of it later) reads only this local cache — it never calls handbook.unimelb.edu.au itself.

## Alternatives considered

- **Live fetch per question** — rejected: makes the demo's response latency and reliability depend on an external site's availability/speed during the actual Open Day event, and means every visitor question sends live traffic to a university system we don't operate, which is inconsiderate at any real usage volume regardless of whether robots.txt technically permits it.
- **Headless browser for ingestion** (to defeat Incapsula) — unnecessary: plain HTTP `GET` with a normal `User-Agent` already returns full content, confirmed directly. Added later only if this stops working.

## Consequences

- Demo runtime has zero dependency on the Handbook site being up or fast.
- Content goes stale between ingestion runs — acceptable for a demo where a human decides when to refresh (`python scripts/ingest_handbook.py`), not appropriate if this needed to reflect same-day Handbook changes.
- Parsing is coupled to the Handbook site's current HTML structure (class names, layout), which could change without notice — see `ASSUMPTIONS.md` A-007. Caught by fixture-based tests failing to extract expected content if it happens, not by any live monitoring.
- This cycle ingests only a small representative set of pages (Diploma in Computing, two subjects) to prove the pipeline; broadening coverage is cheap (add URLs to `PAGES` in the script) and tracked in `BACKLOG.md`.
