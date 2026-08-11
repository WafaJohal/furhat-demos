from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from furhat_demos.config import build_controller
from furhat_demos.control import DemoController
from furhat_demos.webui.demos import DEMOS, find_demo, find_option

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


class SelectionRequest(BaseModel):
    demo_id: str
    option_id: str


def create_app(controller: DemoController | None = None) -> FastAPI:
    controller = controller or build_controller()
    app = FastAPI(title="Furhat Demos")

    @app.get("/api/demos")
    def list_demos():
        return [
            {
                "id": demo.id,
                "name": demo.name,
                "description": demo.description,
                "options": [
                    {"id": o.id, "name": o.name, "description": o.description} for o in demo.options
                ],
            }
            for demo in DEMOS
        ]

    @app.post("/api/select")
    def select(selection: SelectionRequest):
        demo = find_demo(selection.demo_id)
        if demo is None:
            raise HTTPException(status_code=404, detail=f"Unknown demo_id: {selection.demo_id}")
        option = find_option(demo, selection.option_id)
        if option is None:
            raise HTTPException(status_code=404, detail=f"Unknown option_id: {selection.option_id}")
        try:
            controller.start_demo(demo.id, option.id)
        except Exception as exc:
            logger.exception("start_demo failed for demo_id=%s option_id=%s", demo.id, option.id)
            raise HTTPException(
                status_code=503,
                detail="Could not reach the robot — check it's powered on and reachable.",
            ) from exc
        return {"status": "ok", "demo_id": demo.id, "option_id": option.id}

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
