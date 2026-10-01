# Furhat Demos — University of Melbourne

![CI](https://github.com/WafaJohal/furhat-demos/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![version](https://img.shields.io/badge/version-0.4.0-blue)

A Furhat robot demo for University of Melbourne, School of Computing and Information Systems:

**FaceVis** — the [FaceVis](https://github.com/hci-unimelb/FaceVis) research project: the robot's face as a data-visualization medium, driving discrete pre-authored facial states from live air quality data on a world map.

The demo is started from a small **web UI** — a kiosk-style page (tablet or any browser) with a single "Start FaceVis" button. QR-code camera triggering was considered and dropped: Furhat's Remote API has no camera/vision access at all, so reading a QR code would have needed a separate on-robot Kotlin bridge skill just to expose the camera feed. See `docs/adr/0001-webui-over-qr-trigger.md`.

> This project previously also hosted an "Open Day Q&A" RAG demo; it was removed once the Open Day event it supported had passed (see ADR-012). The ADRs and cycle records describing it (0003–0005, 0007, 0009; cycles 004–006, 008, 010) are kept as a historical record even though the code is gone.

## Architecture

The demo is driven by an **external Python control plane** talking to the robot over Furhat's **Realtime API** (WebSocket, port 9000 — not the older REST-style Remote API on port 54321, which the real robot/Virtual didn't have enabled; see ADR-008), fronted by the web UI:

```
[Web UI: browser/tablet] --HTTP--> [FastAPI app] --> [DemoController]
                                                            │
                                                            ▼
                                                    [Furhat robot, via
                                                     Realtime API (WebSocket)]
```

`DemoController` is **runtime state** (`furhat_demos.webui.robot_connection.RobotConnection`), not fixed once at startup: the web UI has a "Robot connection" panel to enter the robot's IP and an optional auth key (required depending on the Realtime API security level configured on the robot) and see live status, backed by `POST /api/robot/connect` and `GET /api/robot/status`. `FURHAT_HOST`/`FURHAT_AUTH_KEY` still work as the startup default — this adds a runtime override on top.

- No successful connection yet — `LoggingDemoController`, which just logs the selection. The default for local UI development with no robot connected.
- After a successful connect (via `FURHAT_HOST`/`FURHAT_AUTH_KEY` at startup, or the UI panel at any time) — `FurhatDemoController`, which connects via `furhat_realtime_api.FurhatClient`, sets an English voice (`request_voice_config(language="en-US")`), makes the robot look at the visitor (`request_attend_user()`), and speaks the FaceVis intro. If the robot drops mid-demo, the web UI's `/api/facevis/start` returns a clean `503` rather than an unhandled-exception traceback.

Connecting enforces a **hard 5-second deadline** on the WebSocket connect+auth handshake, independent of the underlying client's own behavior — same lesson as ADR-006 (found against the old Remote API, re-applied here since nothing guarantees `websockets.connect()` is bounded either).

Clicking "Start FaceVis" on the main page calls `POST /api/facevis/start` and opens `/facevis` in a new tab — a server-rendered Plotly world map (`furhat_demos.facevis.map_page.render_facevis_page`) plotting live air-quality data fetched server-side from WAQI/aqicn.org (needs your own `WAQI_API_TOKEN`; the token never reaches the browser). Clicking a station calls `POST /api/facevis/set_air_quality`, which maps the AQI value to one of the real FaceVis `.charpack` frames (`furhat_demos.facevis.air_quality.aqi_to_face_id`) and drives the robot's face via `request_face_config`, while `DemoController.say()` has the robot speak the station name and its AQI category out loud. On demo start, the robot's intro is grounded in the actual FaceVis research paper (`furhat_demos.facevis.content`) rather than a placeholder. The `.charpack` files themselves must be uploaded to the robot via its own web interface first — that's a manual, one-time step this project's code doesn't do remotely. See ADR-010 and ADR-011.

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
