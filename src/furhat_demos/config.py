from __future__ import annotations

import os

from furhat_remote_api import FurhatRemoteAPI

from furhat_demos.control import DemoController, FurhatDemoController, LoggingDemoController

FURHAT_HOST_ENV_VAR = "FURHAT_HOST"


def build_controller() -> DemoController:
    """Select a DemoController based on environment configuration.

    Set FURHAT_HOST (e.g. "localhost" for Furhat Virtual, or the robot's IP)
    to drive a real Furhat connection. Left unset, falls back to a controller
    that just logs the selection — the default for local UI development.
    """
    host = os.environ.get(FURHAT_HOST_ENV_VAR)
    if not host:
        return LoggingDemoController()
    return FurhatDemoController(FurhatRemoteAPI(host))
