# Backlog

A living list of planned, in-progress, and completed work. Reviewed at the end of every cycle (on each version bump): mark delivered items done, and capture newly discovered work.

## Now (in progress)
<!-- Items being actively worked in the current cycle -->

## Next (planned)
- chore: manually verify the robot connection panel (`/api/robot/connect`) and the live opendemo Q&A turn (listen → answer → say) against the real robot/Furhat Virtual — this environment has no live Furhat to test either path against, only mocked/simulated (an unreachable test IP) in tests
- feat: continuous/multi-question loop for the opendemo Q&A turn instead of one question per button press
- feat: expand `PAGES` in `scripts/ingest_handbook.py` to cover the full set of relevant CIS courses/subjects, not just the 3-page representative set (Diploma in Computing, COMP10001, COMP20003)
- feat: Demo 2 — FaceVis data-viz demo connected to a live Melbourne/Victoria dataset

## Later (ideas / unscheduled)
- Improve `QAEngine` retrieval beyond word-overlap (embeddings/semantic search) — demonstrated to miss relevant content on vocabulary mismatch (e.g. "courses" vs "Bachelor of Science"), see ADR-003 and A-006
- Improve Handbook ingestion content quality: split by section heading instead of whole-page chunks, strip breadcrumb/nav boilerplate lines (e.g. "Handbook / Subjects / <title>" repeated header block) — see A-007
- Demo 2 stretch: continuous FaceCore parameter rendering instead of discrete pre-authored face states
- Demo 1: expand persona roster beyond initial set (more students/group members)
- Consider whether the web UI needs to run reachable over LAN / survive a reboot for the actual event setup (currently local-only, dev-server style)
- No auth on `/api/robot/connect`/`/api/robot/status` — acceptable for a local/LAN kiosk tool, revisit if this ever needs to be reachable beyond that

## Done
- feat: robot connection panel in the web UI — enter an IP, see live status, backed by mutable `RobotConnection` runtime state instead of a fixed startup controller; hard 5s connect deadline independent of the Furhat client's internal retries (found via real testing — see ADR-006) — shipped v0.1.7 (cycle-007)
- feat: live single-turn Q&A on the opendemo option (listen → persona `QAEngine` → say), persona-specific prompts/content, and a clean `503` instead of a raw traceback when the robot is unreachable — shipped v0.1.6 (cycle-006)
- feat: Handbook ingestion pipeline (`furhat_demos.opendemo.handbook`, `scripts/ingest_handbook.py`) — real UniMelb Handbook content replaces the 3 placeholder docs — shipped v0.1.5 (cycle-005)
- feat: `QAEngine` — retrieval-grounded Q&A core for Demo 1, with "I don't know" fallback when nothing relevant is found — shipped v0.1.4 (cycle-004)
- chore: manually verified `FurhatDemoController`'s English-voice selection works on a connected robot — done (cycle-003 follow-up)
- feat: `FurhatDemoController` selects an English voice before speaking (`get_voices`/`set_voice`) — shipped v0.1.3 (cycle-003)
- feat: real `DemoController` (`FurhatDemoController`) driving Furhat via Remote API, selected by `FURHAT_HOST` env var — manually confirmed working against a connected robot — shipped v0.1.2 (cycle-002)
- feat: web UI for demo/option selection (FastAPI + static page, stub `LoggingDemoController`) — shipped v0.1.1 (cycle-001)
- chore: QR code reading spike — dropped in favor of the web UI; superseded, not built. See ADR-001. (cycle-001)
