from __future__ import annotations

import os

from furhat_demos.opendemo.llm_client import LLMClient, OpenAIChatClient

FURHAT_HOST_ENV_VAR = "FURHAT_HOST"
FURHAT_AUTH_KEY_ENV_VAR = "FURHAT_AUTH_KEY"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
WAQI_API_TOKEN_ENV_VAR = "WAQI_API_TOKEN"


def build_llm_client() -> LLMClient | None:
    """Build an OpenAIChatClient when OPENAI_API_KEY is set, else None.

    A None LLMClient means FurhatDemoController skips the listen-and-answer
    step on the opendemo demo (intro only).
    """
    return OpenAIChatClient() if os.environ.get(OPENAI_API_KEY_ENV_VAR) else None
