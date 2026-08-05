# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
