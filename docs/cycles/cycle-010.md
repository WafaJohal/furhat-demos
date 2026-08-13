# Cycle 010 — Remove Wafa Johal persona; add PDF-based admin content loading

- **Date finalized:** 2026-08-12
- **Branch:** `feat/opendemo-admin-pdf-content`
- **Version:** `0.2.0` → `0.3.0` (bump: minor — breaking removal, pre-1.0 convention)

## Plan (as approved)
- **Scope:** remove the Wafa Johal persona entirely (option, intro, system prompt, bio doc); add PDF upload via a new `/admin` page — `POST`/`GET`/`DELETE /api/admin/documents`, extracting text at upload time and saving it into the same content directory `QAEngine` already reads.
- **Files touched:** `webui/demos.py`, `control.py`, `opendemo/personas.py` (Wafa removal); `opendemo/documents.py` (new — extract/save/list/delete), `webui/static/admin.html` (new), `webui/app.py` (new endpoints + injectable `documents_dir`), `webui/static/index.html` (Admin link), `pyproject.toml` (`pypdf`, `python-multipart`).
- **Tests:** removal covered by updated `test_personas.py`/`test_control.py`; new `test_documents.py` (extraction/save/list/delete, including path-traversal and no-text-extracted rejection) using small real PDF fixtures generated once (not a project dependency); endpoint tests using `create_app(documents_dir=tmp_path)` for isolation from the real content directory.

## Assumptions added
- **A-013** (new): uploaded PDFs join one shared content pool rather than being assignable per-persona — reasonable with only one option (`guide`) left after removing Wafa Johal; revisit if personas return.

## Decisions made
- **ADR-009** — unauthenticated `/admin` (matches existing posture), extract-once-at-upload rather than on every load, shared content pool, `documents_dir` as an explicit DI parameter on `create_app()` (needed to keep tests from writing into the real repo content directory — Python binds default-argument values once, not per-call).

## Test & coverage results
- Tests: 76/76 passed
- Coverage: 100% (previous: 100%, floor: 80%)
- Lint / format: pass

## Notes
- Manually verified the admin page renders correctly in a real browser, then did a real upload→list→delete round-trip via `curl` against the actual running app (not just the isolated test suite) to confirm the real endpoint works end-to-end — confirmed no residue left in the real content directory afterward (`git status` clean besides the expected Wafa Johal file removal).
- Caught a real test-isolation bug before writing any tests: the document endpoints' natural default (`data_dir=DATA_DIR`) would have let tests silently write into and delete from the actual repo's content directory during CI. Fixed by making `documents_dir` an explicit, injectable parameter on `create_app()`, mirroring the existing `controller`/`connection` pattern.
- A large reference PDF (`schombs2025dis.pdf`, the source for cycle-011's FaceVis intro content) and the FaceVis charpack archive both live in `assets/`, which is gitignored — neither is committed, consistent with keeping large binaries out of the repo.

## PR
- Link / reference: (added after `gh pr create`)
- Merge status: pending user
