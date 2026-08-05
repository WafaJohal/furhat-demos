# Assumptions

Design assumptions taken as given during development. An assumption is something **treated as true to make progress, which may later prove false** — distinct from a deliberate decision (those live in `docs/adr/`).

Each cycle that introduces new assumptions appends them here. Revisit when an assumption is challenged or invalidated; mark it and note what changed.

## Format

Each entry:

- **ID** — `A-NNN` (sequential)
- **Cycle** — the cycle that introduced it (e.g. cycle-003)
- **Assumption** — stated plainly
- **Rationale** — why we're assuming this
- **Status** — `holding` | `validated` | `invalidated`
- **Notes** — (optional) what would invalidate it; what happened if it changed

---

### A-001
- **Cycle:** cycle-001 (setup)
- **Assumption:** Furhat's camera feed can be externalized (via the Camera & Audio Feeds API / Remote API) with sufficient frame rate and image quality to decode a QR code at typical conversational distance from the robot.
- **Rationale:** Furhat has no native QR/barcode reading; this project depends on streaming raw frames to an external decoder (pyzbar/OpenCV) instead. No public precedent exists for this exact use, so feasibility is unverified.
- **Status:** holding
- **Notes:** This is exactly what the QR reading spike (cycle-001 development) is meant to validate or invalidate. If frame rate/quality is too low, may need a fixed scan distance/lighting setup, a larger printed QR code, or a different trigger mechanism (e.g. NFC/manual selection) for the live demos.

### A-002
- **Cycle:** cycle-001 (setup)
- **Assumption:** A physical Furhat robot will be available and network-reachable for testing during development (not only Furhat Virtual).
- **Rationale:** User confirmed access to a physical unit; the QR spike specifically needs the real camera hardware since Furhat Virtual does not have a real-world camera feed to test against.
- **Status:** holding
- **Notes:** If the physical robot becomes unavailable, camera-feed work would stall until access is restored.

### A-003
- **Cycle:** cycle-001 (setup)
- **Assumption:** Demo 2 (FaceVis) will be built fresh referencing only the public GitHub repo (github.com/hci-unimelb/FaceVis) and published research materials — no access to an internal/original FaceVis codebase or dataset pipeline.
- **Rationale:** User confirmed only public materials are available at this time.
- **Status:** holding
- **Notes:** Revisit if internal FaceVis assets become available later; could change the Demo 2 build approach significantly.
