from __future__ import annotations

import os
from typing import Protocol

_DEFAULT_MODEL = "gpt-4o-mini"


class LLMClient(Protocol):
    def chat(self, *, system: str, user: str) -> str: ...


class OpenAIChatClient:
    def __init__(self, api_key: str | None = None, model: str = _DEFAULT_MODEL) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._model = model

    def chat(self, *, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content or ""
