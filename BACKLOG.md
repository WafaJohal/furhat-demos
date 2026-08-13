# Backlog

A living list of planned, in-progress, and completed work. Reviewed at the end of every cycle (on each version bump): mark delivered items done, and capture newly discovered work.

## Now (in progress)
<!-- Items being actively worked in the current cycle -->

## Next (planned)
- chore: manually verify the FaceVis flow end-to-end against a real `WAQI_API_TOKEN` and the actual robot with the charpacks uploaded — this environment has neither, so the map/AQI parsing and charpack selection are tested only against recalled response shapes and mocked robot calls (see A-014, A-015)
- feat: expand `PAGES` in `scripts/ingest_handbook.py` to cover the full set of relevant CIS courses/subjects, not just the 3-page representative set (Diploma in Computing, COMP10001, COMP20003)
- feat: FaceVis follow-up — let the map page drive datasets beyond air quality (e.g. cholesterol, from the same paper); per-persona document assignment for admin-uploaded PDFs (currently all uploads join one shared pool)

## Later (ideas / unscheduled)
- Improve `QAEngine` retrieval beyond word-overlap (embeddings/semantic search) — demonstrated to miss relevant content on vocabulary mismatch (e.g. "courses" vs "Bachelor of Science"), see ADR-003 and A-006
- Improve Handbook ingestion content quality: split by section heading instead of whole-page chunks, strip breadcrumb/nav boilerplate lines (e.g. "Handbook / Subjects / <title>" repeated header block) — see A-007
- Demo 2 stretch: continuous FaceCore parameter rendering (`request_face_params`) instead of discrete pre-authored charpack frames
- Consider whether the web UI needs to run reachable over LAN / survive a reboot for the actual event setup (currently local-only, dev-server style)
- No auth on `/api/robot/connect`/`/api/robot/status`/`/admin`/`/facevis` — acceptable for a local/LAN kiosk tool, revisit if this ever needs to be reachable beyond that
- The exit-phrase list for ending the Q&A loop is a coarse heuristic (e.g. "thanks" was deliberately left out to avoid false-triggering on "thanks, and also...") — revisit if real usage shows it's mis-ending or not ending when it should
- Harden `RobotConnection.connect()` beyond the WS+auth handshake alone — observed a false-positive "connected" against an unrelated service coincidentally speaking a Furhat-shaped protocol on port 9000 in the dev sandbox (environment-specific artifact, not reproduced on real hardware, but suggests a follow-up call like `request_voice_status()` after connect would be a more robust "is this actually Furhat" check
- Investigate real Furhat Realtime API `listen()`/`request_listen_start()` return format further for edge cases (e.g. partial results, `stop_*` config options) now that the migration is confirmed working — see A-008, A-011
- Get the user's sign-off on the AQI-to-charpack mapping (band boundaries, "Very Unhealthy + Hazardous combined onto AirHazard") once seen live — see A-015

## Done
- feat: FaceVis — clicking a map station now also has the robot speak the station name and AQI category (`DemoController.say()`) alongside the existing face-driving behavior — shipped v0.3.2 (cycle-011 follow-up)
- feat: FaceVis — `/facevis` map page (server-rendered Plotly + WAQI live air quality; Leaflet/OpenStreetMap tried first, dropped per ADR-011), charpack-driven robot face (`request_face_config`, reusing the real FaceVis charpack assets), paper-grounded spoken intro on demo start — shipped v0.3.1 (cycle-011)
- feat: removed the Wafa Johal persona/button; added PDF-based content loading via an admin tab (`/admin`, `POST`/`GET`/`DELETE /api/admin/documents`) — uploaded PDFs join the same content pool `QAEngine` already reads — shipped v0.3.0 (cycle-010)
- feat: migrated robot connection from the REST-style Remote API (port 54321) to the Realtime API (WebSocket, port 9000) — the real robot/Virtual only had the latter enabled; adds native auth-key support, simplifies voice selection to one call, adds `request_attend_user()` — confirmed working by the user against a real connection — shipped v0.2.0 (cycle-009)
- feat: continuous multi-question Q&A loop for the opendemo demo (was one question per button press) — exit phrase, double-silence, or 10-turn cap all end the loop with a goodbye — shipped v0.1.8 (cycle-008)
- feat: robot connection panel in the web UI — enter an IP, see live status, backed by mutable `RobotConnection` runtime state instead of a fixed startup controller; hard 5s connect deadline independent of the Furhat client's internal retries (found via real testing — see ADR-006) — shipped v0.1.7 (cycle-007)
- feat: live single-turn Q&A on the opendemo option (listen → persona `QAEngine` → say), persona-specific prompts/content, and a clean `503` instead of a raw traceback when the robot is unreachable — shipped v0.1.6 (cycle-006)
- feat: Handbook ingestion pipeline (`furhat_demos.opendemo.handbook`, `scripts/ingest_handbook.py`) — real UniMelb Handbook content replaces the 3 placeholder docs — shipped v0.1.5 (cycle-005)
- feat: `QAEngine` — retrieval-grounded Q&A core for Demo 1, with "I don't know" fallback when nothing relevant is found — shipped v0.1.4 (cycle-004)
- chore: manually verified `FurhatDemoController`'s English-voice selection works on a connected robot — done (cycle-003 follow-up)
- feat: `FurhatDemoController` selects an English voice before speaking (`get_voices`/`set_voice`) — shipped v0.1.3 (cycle-003)
- feat: real `DemoController` (`FurhatDemoController`) driving Furhat via Remote API, selected by `FURHAT_HOST` env var — manually confirmed working against a connected robot — shipped v0.1.2 (cycle-002)
- feat: web UI for demo/option selection (FastAPI + static page, stub `LoggingDemoController`) — shipped v0.1.1 (cycle-001)
- chore: QR code reading spike — dropped in favor of the web UI; superseded, not built. See ADR-001. (cycle-001)
