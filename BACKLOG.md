# Backlog

A living list of planned, in-progress, and completed work. Reviewed at the end of every cycle (on each version bump): mark delivered items done, and capture newly discovered work.

## Now (in progress)
<!-- Items being actively worked in the current cycle -->

## Next (planned)
- feat: replace real Open Day pamphlet/curriculum content for the placeholder docs in `src/furhat_demos/opendemo/data/` — need actual source material from the user
- feat: persona-specific system prompts for `QAEngine` (generic guide vs Wafa Johal persona), and wire `QAEngine` into `FurhatDemoController`'s opendemo option (text answer → `say()`; consider `listen()` for voice input, which Furhat's Remote API already exposes)
- feat: Demo 2 — FaceVis data-viz demo connected to a live Melbourne/Victoria dataset

## Later (ideas / unscheduled)
- Improve `QAEngine` retrieval beyond word-overlap (embeddings/semantic search) — demonstrated to miss relevant content on vocabulary mismatch (e.g. "courses" vs "Bachelor of Science"), see ADR-003 and A-006
- Demo 2 stretch: continuous FaceCore parameter rendering instead of discrete pre-authored face states
- Demo 1: expand persona roster beyond initial set (more students/group members)
- Consider whether the web UI needs to run reachable over LAN / survive a reboot for the actual event setup (currently local-only, dev-server style)

## Done
- feat: `QAEngine` — retrieval-grounded Q&A core for Demo 1, with "I don't know" fallback when nothing relevant is found — shipped v0.1.4 (cycle-004)
- chore: manually verified `FurhatDemoController`'s English-voice selection works on a connected robot — done (cycle-003 follow-up)
- feat: `FurhatDemoController` selects an English voice before speaking (`get_voices`/`set_voice`) — shipped v0.1.3 (cycle-003)
- feat: real `DemoController` (`FurhatDemoController`) driving Furhat via Remote API, selected by `FURHAT_HOST` env var — manually confirmed working against a connected robot — shipped v0.1.2 (cycle-002)
- feat: web UI for demo/option selection (FastAPI + static page, stub `LoggingDemoController`) — shipped v0.1.1 (cycle-001)
- chore: QR code reading spike — dropped in favor of the web UI; superseded, not built. See ADR-001. (cycle-001)
