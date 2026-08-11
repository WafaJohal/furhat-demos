# Furhat Demos — University of Melbourne

![CI](https://github.com/WafaJohal/furhat-demos/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![version](https://img.shields.io/badge/version-0.1.7-blue)

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

`DemoController` is now **runtime state** (`furhat_demos.webui.robot_connection.RobotConnection`), not fixed once at startup: the web UI has a "Robot connection" panel to enter the robot's IP and see live status, backed by `POST /api/robot/connect` and `GET /api/robot/status`. `FURHAT_HOST` still works exactly as before as the startup default — this adds a runtime override on top.

- No successful connection yet — `LoggingDemoController`, which just logs the selection. The default for local UI development with no robot connected.
- After a successful connect (via `FURHAT_HOST` at startup, or the UI panel at any time) — `FurhatDemoController`, which connects via `furhat_remote_api`, ensures an English voice is selected (language is tied to voice choice in Furhat's API), speaks an intro for the selected demo/option, and — for the opendemo demos, when `OPENAI_API_KEY` is also set — listens once for a question, answers it via that persona's `QAEngine`, and speaks the answer. One question per button press, not an ongoing conversation (see `BACKLOG.md`). If the robot drops mid-demo, the web UI's `/api/select` returns a clean `503` rather than an unhandled-exception traceback.

Connecting probes the robot (`get_voices`) with a **hard 5-second deadline** enforced independently of the underlying HTTP client — real-world testing found the client's own internal retry behavior means a per-call timeout alone doesn't bound total latency on an unreachable-but-not-actively-refusing host (see ADR-006).

Demo 1's Q&A core is `furhat_demos.opendemo.QAEngine`: it retrieves relevant chunks by word-overlap scoring, then answers via an injected `LLMClient` (`OpenAIChatClient` for real use, needs `OPENAI_API_KEY`) — or returns a fixed "I don't know" style response without calling the LLM at all when nothing relevant is found. `furhat_demos.opendemo.personas.build_qa_engine(persona_id, llm_client)` builds one per persona: `guide` uses the general Handbook content; `wafa-johal` uses Handbook content plus a dedicated bio doc (`data/personas/wafa-johal.md` — the Handbook doesn't cover individual researchers), with her own system prompt.

The general content in `data/` is real University of Melbourne Handbook material (handbook.unimelb.edu.au), cached ahead of time — run `python scripts/ingest_handbook.py` to (re)generate it. The live demo never calls the Handbook site itself, only this local cache. Currently covers a small representative set (Diploma in Computing, Foundations of Computing, Algorithms and Data Structures); expand `PAGES` in that script to broaden coverage.

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

FURHAT_HOST=localhost uvicorn furhat_demos.webui.app:app --reload   # drive Furhat Virtual instead
```

Coverage floor: **80%** (ratcheting — see CI).
