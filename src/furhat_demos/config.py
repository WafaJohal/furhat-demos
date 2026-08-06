from __future__ import annotations

import os

from furhat_remote_api import FurhatRemoteAPI

from furhat_demos.control import DemoController, FurhatDemoController, LoggingDemoController
from furhat_demos.opendemo.llm_client import LLMClient, OpenAIChatClient

FURHAT_HOST_ENV_VAR = "FURHAT_HOST"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"


def build_llm_client() -> LLMClient | None:
    """Build an OpenAIChatClient when OPENAI_API_KEY is set, else None.

    A None LLMClient means FurhatDemoController skips the listen-and-answer
    step on the opendemo demo (intro only).
    """
    return OpenAIChatClient() if os.environ.get(OPENAI_API_KEY_ENV_VAR) else None


def build_controller() -> DemoController:
    """Select a DemoController based on environment configuration.

    Set FURHAT_HOST (e.g. "localhost" for Furhat Virtual, or the robot's IP)
    to drive a real Furhat connection. Left unset, falls back to a controller
    that just logs the selection — the default for local UI development.

    Additionally set OPENAI_API_KEY to enable the live Q&A turn on the opendemo
    demo; left unset, FurhatDemoController still speaks its intro but skips
    the listen-and-answer step.
    """
    host = os.environ.get(FURHAT_HOST_ENV_VAR)
    if not host:
        return LoggingDemoController()
    return FurhatDemoController(FurhatRemoteAPI(host), llm_client=build_llm_client())
