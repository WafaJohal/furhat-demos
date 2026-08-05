# ADR-001: Web UI for demo/option selection, instead of a QR-code camera trigger

- **Status:** accepted
- **Date:** 2026-08-05
- **Cycle:** cycle-001

## Context

The original spec for both demos included triggering/selecting them by having a visitor show a QR code to the robot's camera (e.g. a persona card, or a dataset selector). Furhat has no native QR/barcode reading. Investigation during cycle-001 planning found:

- Furhat's Camera & Audio Feeds API (which can expose camera frames externally) is only callable from *within* an on-robot Kotlin skill — it is not part of the external control surface.
- The official `furhat_remote_api` Python package was inspected directly (its public method list) and confirmed to expose **no camera or vision endpoints at all** — only speech (`say`), gestures, face/voice/LED control, `listen` (speech recognition), users, and visibility.
- The only documented precedent for getting frames off the robot (`FurhatRobotics/camerafeed-demo`) pairs a small on-robot Kotlin skill with an external Python process — i.e. QR reading would require standing up a second toolchain (Kotlin/Gradle/Furhat SDK) purely to expose the camera feed, on top of the physical robot's own deployment step.

The user decided to drop the QR-triggered flow before that infrastructure was built.

## Decision

We will trigger and configure both demos through a small **web UI** (FastAPI backend + static HTML/JS page) instead of QR-code scanning. A visitor (or staff member) picks a demo and an option (persona, dataset, etc.) from the page, which calls a `DemoController` interface to start it. This keeps the whole project in one ecosystem (Python) with no on-robot Kotlin bridge skill required for triggering.

## Alternatives considered

- **QR code via robot camera** — the originally spec'd approach; rejected because it requires building and maintaining a second on-robot Kotlin skill just to expose frames externally, for a capability (camera access) Furhat's Remote API doesn't provide at all.
- **NFC/manual physical selector** — not explored in depth; web UI was preferred since it's zero extra hardware and supports richer, multi-option selection (persona *and* dataset choice) more easily than a single QR payload would.

## Consequences

- Simpler architecture: one Python control plane, no JVM/Kotlin toolchain needed for this project (yet — Furhat skills built directly for the robot may still end up needing one later, but not for triggering).
- Loses the "walk up and scan" novelty of the original concept; selection now requires a screen/tablet near the robot.
- `ASSUMPTIONS.md` A-001 (camera feed externalization for QR) is marked invalidated/superseded rather than tested.
- Frees up the "Next" backlog to focus on the real `DemoController` implementation (Remote/Realtime API integration) rather than camera/vision plumbing.
