# Furhat Demos — University of Melbourne

![CI](https://github.com/WafaJohal/furhat-demos/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![version](https://img.shields.io/badge/version-0.1.0-blue)

Two Furhat robot demos for University of Melbourne, School of Computing and Information Systems:

1. **Open Day Q&A** — Furhat answers Open Day questions grounded on curriculum/pamphlet documents (RAG), with switchable personas (a generic guide, plus researcher personas such as Wafa Johal and her group). Says "I don't know" rather than guessing when it lacks grounding.
2. **FaceVis** — the [FaceVis](https://github.com/hci-unimelb/FaceVis) research project, connecting the robot's face to a live Melbourne/Victoria dataset as a data-visualization medium.

Both demos are triggerable by scanning a QR code with the robot's camera — a feature Furhat has no native support for, so this repo builds it as shared infrastructure (camera feed → external QR decode) rather than a per-demo hack.

## Architecture

Furhat's on-robot Kotlin skill SDK doesn't expose QR/barcode reading or the custom LLM/vision logic these demos need. Instead, both demos are driven by an **external Python control plane** talking to the robot over Furhat's Remote/Realtime API:

```
[Furhat robot] <--camera feed / control--> [Python process]
                                                  ├── QR decoder (pyzbar/opencv)
                                                  ├── LLM client (OpenAI API) + RAG   [Demo 1]
                                                  ├── Persona / face-state controller  [Demo 1 & 2]
                                                  └── Melbourne/Victoria data feed     [Demo 2]
```

See `docs/adr/` for the recorded reasoning behind this and other architectural decisions as they're made.

## Development

This project follows a cycle-based workflow — see `BACKLOG.md` for planned work, `ASSUMPTIONS.md` for open assumptions, `docs/adr/` for decisions, and `docs/cycles/` for a record of each development cycle.

```bash
pip install -e ".[dev]"
pytest          # run tests with coverage
ruff check .     # lint
ruff format .    # format
pre-commit install   # enable local pre-commit hooks
```

Coverage floor: **80%** (ratcheting — see CI).
