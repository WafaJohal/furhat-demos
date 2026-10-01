from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
    aqi_category_label,
    aqi_to_face_id,
    fetch_stations,
)
from furhat_demos.facevis.map_page import render_facevis_page
from furhat_demos.webui.robot_connection import RobotConnection

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


class ConnectRequest(BaseModel):
    host: str
    auth_key: str | None = None


class AirQualityRequest(BaseModel):
    aqi: float
    name: str | None = None


def _default_fetch_stations() -> list[Station]:
    token = os.environ.get(WAQI_API_TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f"{WAQI_API_TOKEN_ENV_VAR} is not set")
    return fetch_stations(RequestsHttpClient(), token)


def create_app(
    controller: DemoController | None = None,
    connection: RobotConnection | None = None,
    stations_fetcher: Callable[[], list[Station]] | None = None,
) -> FastAPI:
    connection = connection or RobotConnection()
    fetch_air_quality_stations = stations_fetcher or _default_fetch_stations
    if controller is not None:
        connection.controller = controller
    elif os.environ.get(FURHAT_HOST_ENV_VAR):
        connection.connect(os.environ[FURHAT_HOST_ENV_VAR], os.environ.get(FURHAT_AUTH_KEY_ENV_VAR))

    app = FastAPI(title="Furhat Demos")

    @app.post("/api/facevis/start")
    def start_facevis():
        try:
            connection.controller.start_demo("facevis", "air-quality")
        except Exception as exc:
            logger.exception("start_demo failed for the FaceVis demo")
            raise HTTPException(
                status_code=503,
                detail="Could not reach the robot — check it's powered on and reachable.",
            ) from exc
        return {"status": "ok"}

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
        location = request.name or "this location"
        category = aqi_category_label(request.aqi)
        connection.controller.say(
            f"In {location}, the air quality index is {request.aqi:g} — {category}."
        )
        return {"status": "ok", "face_id": face_id}

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
