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
- **Status:** invalidated
- **Notes:** Superseded in cycle-001 (development): the QR-based trigger was dropped in favor of a web UI selector before this was tested, and confirmed moot — the official `furhat_remote_api` package exposes zero camera/vision endpoints, so this assumption's premise (external camera access via Remote API) doesn't hold anyway. See ADR-001.

### A-002
- **Cycle:** cycle-001 (setup)
- **Assumption:** A physical Furhat robot will be available and network-reachable for testing during development (not only Furhat Virtual).
- **Rationale:** User confirmed access to a physical unit. No longer tied to camera-feed work specifically (QR dropped, see A-001), but still relevant once a real `DemoController` drives the robot via Remote/Realtime API in upcoming cycles.
- **Status:** holding
- **Notes:** If the physical robot becomes unavailable, live robot-control work would stall until access is restored; Furhat Virtual can stand in for control-API testing (speech, gestures, persona) in the meantime. Observed directly during cycle-006 testing: user hit a "No route to host" error connecting to the robot's IP (likely a hotspot-network routing issue on the test machine, not a code bug) — motivated the cycle-006 addition of a clean `503` response instead of a raw traceback when this happens.

### A-003
- **Cycle:** cycle-001 (setup)
- **Assumption:** Demo 2 (FaceVis) will be built fresh referencing only the public GitHub repo (github.com/hci-unimelb/FaceVis) and published research materials — no access to an internal/original FaceVis codebase or dataset pipeline.
- **Rationale:** User confirmed only public materials are available at this time.
- **Status:** holding
- **Notes:** Revisit if internal FaceVis assets become available later; could change the Demo 2 build approach significantly.

### A-004
- **Cycle:** cycle-002
- **Assumption:** `FurhatDemoController`'s connection to a real Furhat instance (`furhat_remote_api.FurhatRemoteAPI(host).say(...)`) works as documented against Furhat Virtual and the physical robot, not just against the mocked `RemoteApi` used in tests.
- **Rationale:** This environment has no live Furhat/Furhat Virtual instance to test against; the controller was verified by construction (no network call on init, confirmed) and by unit tests with a fake remote-API object, not by an actual `.say()` round-trip.
- **Status:** validated
- **Notes:** User manually confirmed in cycle-003 development: connecting via `FURHAT_HOST` and pressing a web UI option makes a connected robot speak.

### A-005
- **Cycle:** cycle-003
- **Assumption:** The English-voice selection added in cycle-003 (`get_voices()` → pick a voice whose `language` starts with "en" → `set_voice(name=...)`) actually results in the robot speaking with an English voice on a real connection, not just in the mocked unit tests.
- **Rationale:** No live Furhat/Furhat Virtual instance in this environment to confirm the real `Voice.language` values or that `set_voice` visibly changes the spoken accent/language. Implemented defensively (warns and continues if no match or lookup fails) precisely because this was unverified at write time.
- **Status:** validated
- **Notes:** User manually confirmed it works on a connected robot.

### A-006
- **Cycle:** cycle-004
- **Assumption:** Plain word-overlap retrieval (no stemming, no embeddings) is good enough to find relevant chunks for realistic Open Day questions.
- **Rationale:** Chosen to keep this cycle fully offline-testable (no embeddings API calls needed in CI) and simple to reason about. Demonstrated *false* during manual smoke-testing this cycle: "What courses do you offer?" returned the "I don't know" fallback because the placeholder doc used "Bachelor of Science"/"Master of..." rather than the literal word "courses" — fixed for that specific case by editing the placeholder doc, but the underlying brittleness (vocabulary mismatch) is structural, not fixed.
- **Status:** invalidated (for the general case; works for close vocabulary matches only)
- **Notes:** See ADR-003. Tracked in `BACKLOG.md` as a "Later" item — move to embeddings/semantic retrieval before this is trusted against real, unedited pamphlet content where question phrasing won't always match source wording.

### A-007
- **Cycle:** cycle-005
- **Assumption:** The Handbook site's HTML structure (CSS class names like `search-result-item__anchor`, the `#main-content`/`.layout-sidebar__side` layout used to strip nav/sidebar boilerplate) stays stable enough that `furhat_demos.opendemo.handbook`'s parsers keep working without maintenance.
- **Rationale:** Parsers were written against real pages fetched 2026-08-06 and are tested only against saved fixtures from that date — there's no live contract with the Handbook site, just observed structure. A redesign of the site would silently break parsing (likely returning empty/garbled text rather than an obvious error).
- **Status:** holding
- **Notes:** Also flagging a related, lower-severity issue found during this cycle: ingested chunks are coarse (whole-page, not split by section — the source pages don't have blank-line boundaries between subsections) and carry breadcrumb/nav text at the top of each chunk. Both are content-quality issues, not correctness bugs; tracked in `BACKLOG.md`.

### A-008
- **Cycle:** cycle-006
- **Assumption:** `remote_api.listen()`'s real behavior (blocking until speech or timeout, `Status.message` containing recognized text or one of `SILENCE`/`INTERRUPTED`/`FAILED`) matches Furhat's documented behavior closely enough for `FurhatDemoController._run_single_qa_turn` to work as designed on a real connection.
- **Rationale:** No live Furhat/Furhat Virtual instance in this environment to test the `listen()` path — only mocked in tests (`FakeRemoteApi.listen()` returning a canned `FakeListenResult`). Real speech recognition quality/latency/timeout behavior is unverified.
- **Status:** holding
- **Notes:** Needs manual verification by the user against a real connection — including whether blocking the intro (`say(..., blocking=True)`) actually prevents `listen()` from picking up the tail of the robot's own speech as intended.
