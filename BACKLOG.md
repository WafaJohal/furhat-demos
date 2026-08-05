# Backlog

A living list of planned, in-progress, and completed work. Reviewed at the end of every cycle (on each version bump): mark delivered items done, and capture newly discovered work.

## Now (in progress)
<!-- Items being actively worked in the current cycle -->

## Next (planned)
- feat: Demo 1 — Open Day Q&A persona skill (RAG over pamphlet/curriculum docs, persona switching, "I don't know" fallback)
- feat: Demo 2 — FaceVis data-viz demo connected to a live Melbourne/Victoria dataset
- chore: manually verify `FurhatDemoController` against Furhat Virtual (and later the physical robot) — not exercised in CI, mocked only

## Later (ideas / unscheduled)
- Demo 2 stretch: continuous FaceCore parameter rendering instead of discrete pre-authored face states
- Demo 1: expand persona roster beyond initial set (more students/group members)
- Consider whether the web UI needs to run reachable over LAN / survive a reboot for the actual event setup (currently local-only, dev-server style)

## Done
- feat: real `DemoController` (`FurhatDemoController`) driving Furhat via Remote API, selected by `FURHAT_HOST` env var — shipped v0.1.2 (cycle-002)
- feat: web UI for demo/option selection (FastAPI + static page, stub `LoggingDemoController`) — shipped v0.1.1 (cycle-001)
- chore: QR code reading spike — dropped in favor of the web UI; superseded, not built. See ADR-001. (cycle-001)
