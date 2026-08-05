# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-08-05
### Added
- `QAEngine` (`furhat_demos.opendemo.qa`): a retrieval-grounded Q&A core for
  Demo 1. Retrieves relevant chunks from placeholder Open Day/curriculum docs
  by word-overlap scoring, then answers via an injected `LLMClient` — or
  returns a fixed "I don't know" style response without calling the LLM at
  all when no relevant chunk is found.
- `OpenAIChatClient`, a real `LLMClient` implementation using the `openai`
  package (needs `OPENAI_API_KEY`); tests use a fake client, no network calls.
- Placeholder Open Day/curriculum content under `src/furhat_demos/opendemo/data/`.

### Known limitation
- Retrieval is plain word-overlap (no stemming/embeddings), so it's brittle
  to vocabulary mismatch between the question and the source text — see
  ADR-003 and `ASSUMPTIONS.md` A-006.

## [0.1.3] - 2026-08-05
### Added
- `FurhatDemoController` now ensures an English voice is selected on the
  connected robot (via `get_voices`/`set_voice`) before it speaks, since
  language is tied to voice choice rather than a separate `say()` parameter.
  Selection happens once per controller instance; if no English voice is
  found or the lookup fails, it logs a warning and speaks anyway rather than
  blocking the demo.

## [0.1.2] - 2026-08-05
### Added
- `FurhatDemoController`, a real `DemoController` that speaks a placeholder
  intro via Furhat's Remote API (`furhat_remote_api`) for each demo/option.
- `FURHAT_HOST` environment variable to select it; unset, the app keeps
  defaulting to `LoggingDemoController` for local UI development.

## [0.1.1] - 2026-08-05
### Added
- Web UI (FastAPI + static page) for picking a demo and an option, backed by a
  pluggable `DemoController` interface (stub `LoggingDemoController` for now).

### Changed
- Dropped the QR-code camera trigger in favor of the web UI: Furhat's Remote
  API has no camera/vision access at all, so QR reading would have required
  a separate on-robot Kotlin bridge skill. See ADR-001.

## [0.1.0] - 2026-08-05
### Added
- Initial project scaffold.
