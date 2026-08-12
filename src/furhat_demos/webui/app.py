from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from furhat_demos.config import (
    FURHAT_AUTH_KEY_ENV_VAR,
    FURHAT_HOST_ENV_VAR,
    WAQI_API_TOKEN_ENV_VAR,
)
from furhat_demos.control import DemoController
from furhat_demos.facevis.air_quality import (
    RequestsHttpClient,
    Station,
    aqi_to_face_id,
    fetch_stations,
)
from furhat_demos.facevis.map_page import render_facevis_page
from furhat_demos.opendemo.documents import (
    delete_uploaded_document,
    list_uploaded_documents,
    save_uploaded_pdf,
)
from furhat_demos.opendemo.qa import DATA_DIR
from furhat_demos.webui.demos import DEMOS, find_demo, find_option
from furhat_demos.webui.robot_connection import RobotConnection

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


class SelectionRequest(BaseModel):
    demo_id: str
    option_id: str


class ConnectRequest(BaseModel):
    host: str
    auth_key: str | None = None


class AirQualityRequest(BaseModel):
    aqi: float


def _default_fetch_stations() -> list[Station]:
    token = os.environ.get(WAQI_API_TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f"{WAQI_API_TOKEN_ENV_VAR} is not set")
    return fetch_stations(RequestsHttpClient(), token)


def create_app(
    controller: DemoController | None = None,
    connection: RobotConnection | None = None,
    documents_dir: Path | None = None,
    stations_fetcher: Callable[[], list[Station]] | None = None,
) -> FastAPI:
    connection = connection or RobotConnection()
    docs_dir = documents_dir or DATA_DIR
    fetch_air_quality_stations = stations_fetcher or _default_fetch_stations
    if controller is not None:
        connection.controller = controller
    elif os.environ.get(FURHAT_HOST_ENV_VAR):
        connection.connect(os.environ[FURHAT_HOST_ENV_VAR], os.environ.get(FURHAT_AUTH_KEY_ENV_VAR))

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
            connection.controller.start_demo(demo.id, option.id)
        except Exception as exc:
            logger.exception("start_demo failed for demo_id=%s option_id=%s", demo.id, option.id)
            raise HTTPException(
                status_code=503,
                detail="Could not reach the robot — check it's powered on and reachable.",
            ) from exc
        return {"status": "ok", "demo_id": demo.id, "option_id": option.id}

    @app.post("/api/robot/connect")
    def connect_robot(request: ConnectRequest):
        state = connection.connect(request.host, request.auth_key)
        if not state.connected:
            raise HTTPException(status_code=502, detail=state.error or "Could not connect.")
        return {"host": state.host, "connected": state.connected}

    @app.get("/api/robot/status")
    def robot_status():
        state = connection.state
        return {
            "host": state.host,
            "connected": state.connected,
            "error": state.error,
            "checked_at": state.checked_at,
        }

    @app.get("/admin")
    def admin_page():
        return FileResponse(STATIC_DIR / "admin.html")

    @app.get("/api/admin/documents")
    def get_admin_documents():
        return [{"filename": doc.filename} for doc in list_uploaded_documents(data_dir=docs_dir)]

    @app.post("/api/admin/documents")
    async def upload_admin_document(file: UploadFile):
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        pdf_bytes = await file.read()
        try:
            doc = save_uploaded_pdf(file.filename or "document.pdf", pdf_bytes, data_dir=docs_dir)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"filename": doc.filename}

    @app.delete("/api/admin/documents/{filename}")
    def delete_admin_document(filename: str):
        try:
            deleted = delete_uploaded_document(filename, data_dir=docs_dir)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Unknown document: {filename}")
        return {"status": "ok", "filename": filename}

    @app.get("/facevis", response_class=HTMLResponse)
    def facevis_page():
        try:
            stations = fetch_air_quality_stations()
        except Exception as exc:
            logger.exception("Failed to fetch air quality stations")
            return render_facevis_page(None, error=str(exc))
        return render_facevis_page(stations)

    @app.post("/api/facevis/set_air_quality")
    def set_air_quality(request: AirQualityRequest):
        face_id = aqi_to_face_id(request.aqi)
        connection.controller.set_face(face_id)
        return {"status": "ok", "face_id": face_id}

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
