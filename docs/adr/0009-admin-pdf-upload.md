# ADR-009: Admin PDF upload — unauthenticated tab, shared content pool, convert-at-upload

- **Status:** accepted
- **Date:** 2026-08-12
- **Cycle:** cycle-010

## Context

The user asked to remove the Wafa Johal persona and instead be able to load additional Open Day content as PDFs, "maybe only through an admin tab." This needed a few concrete design calls: where the admin UI lives, whether uploaded content is shared or persona-specific, and how/when PDF text gets extracted.

## Decision

1. **A separate, unlinked-from-nowhere-but-discoverable `/admin` page** — not password-protected. Consistent with this project's existing posture (`/api/robot/connect` and `/api/robot/status` are also unauthenticated) for a local/LAN kiosk tool.
2. **Extract text once, at upload time**, not on every read. `POST /api/admin/documents` runs the PDF through `pypdf` immediately and writes the result as a `.md` file (`uploaded-<slug>.md`) into the same directory as the Handbook content. `QAEngine`'s existing `load_chunks()` picks it up automatically — no changes needed there.
3. **Uploaded documents join one shared content pool**, not assigned to a specific persona/option. With Wafa Johal removed, there's currently only one opendemo option, so per-document persona assignment isn't a meaningful distinction yet.
4. **`documents_dir` is an explicit, injectable parameter on `create_app()`** (mirroring the existing `controller`/`connection` DI pattern) rather than a module-level default — this was necessary to keep tests from writing into the real content directory, since Python binds default-argument values once at function definition, not per-call.

## Alternatives considered

- **Extract text on every `QAEngine` load instead of at upload time** — rejected: repeats PDF parsing work on every app start for no benefit, and couples `qa.py`'s chunk loader to PDF parsing when converting once and writing plain markdown keeps that loader untouched.
- **Password-protect `/admin`** — not requested, and would need a real auth story (sessions, credentials) disproportionate to a local kiosk tool; tracked as a `BACKLOG.md` item if this ever needs to be reachable beyond a trusted local network.

## Consequences

- Uploading a PDF with no extractable text (e.g. scanned images with no text layer) fails clearly at upload time (`400`, "No extractable text found") rather than silently producing an empty, useless chunk file later.
- Deleting a document only removes the converted `.md` file — the original PDF was never kept.
- If personas return, the "shared pool" design (A-013) will need revisiting — not solved now, deliberately deferred.
