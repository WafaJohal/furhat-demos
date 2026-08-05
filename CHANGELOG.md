# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
