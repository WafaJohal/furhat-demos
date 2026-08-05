from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from furhat_demos.control import DemoController, LoggingDemoController
from furhat_demos.webui.demos import DEMOS, find_demo, find_option

STATIC_DIR = Path(__file__).parent / "static"


class SelectionRequest(BaseModel):
    demo_id: str
    option_id: str


def create_app(controller: DemoController | None = None) -> FastAPI:
    controller = controller or LoggingDemoController()
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
        controller.start_demo(demo.id, option.id)
        return {"status": "ok", "demo_id": demo.id, "option_id": option.id}

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
