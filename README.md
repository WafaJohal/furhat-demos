# Furhat Demos — University of Melbourne

![CI](https://github.com/WafaJohal/furhat-demos/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![version](https://img.shields.io/badge/version-0.1.1-blue)

Two Furhat robot demos for University of Melbourne, School of Computing and Information Systems:

1. **Open Day Q&A** — Furhat answers Open Day questions grounded on curriculum/pamphlet documents (RAG), with switchable personas (a generic guide, plus researcher personas such as Wafa Johal and her group). Says "I don't know" rather than guessing when it lacks grounding.
2. **FaceVis** — the [FaceVis](https://github.com/hci-unimelb/FaceVis) research project, connecting the robot's face to a live Melbourne/Victoria dataset as a data-visualization medium.

Both demos are started from a small **web UI** — a kiosk-style page (tablet or any browser) listing the demos and their options (persona, dataset, etc.). QR-code camera triggering was considered and dropped: Furhat's Remote API has no camera/vision access at all, so reading a QR code would have needed a separate on-robot Kotlin bridge skill just to expose the camera feed. See `docs/adr/0001-webui-over-qr-trigger.md`.

## Architecture

Both demos are driven by an **external Python control plane** talking to the robot over Furhat's Remote/Realtime API, fronted by the web UI:

```
[Web UI: browser/tablet] --HTTP--> [FastAPI app] --> [DemoController]
                                                            │
                                                            ▼
                                                    [Furhat robot, via
                                                     Remote/Realtime API]
```

Currently `DemoController` is a stub (`LoggingDemoController`) that just logs the selection — it gets replaced with a real implementation (LLM/RAG for Demo 1, persona/face-state control for Demo 1 & 2, Melbourne/Victoria data feed for Demo 2) in upcoming cycles.

See `docs/adr/` for the recorded reasoning behind this and other architectural decisions as they're made.

## Development

This project follows a cycle-based workflow — see `BACKLOG.md` for planned work, `ASSUMPTIONS.md` for open assumptions, `docs/adr/` for decisions, and `docs/cycles/` for a record of each development cycle.

```bash
pip install -e ".[dev]"
pytest          # run tests with coverage
ruff check .     # lint
ruff format .    # format
pre-commit install   # enable local pre-commit hooks

uvicorn furhat_demos.webui.app:app --reload   # run the web UI at http://127.0.0.1:8000
```

Coverage floor: **80%** (ratcheting — see CI).
