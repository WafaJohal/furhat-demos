from __future__ import annotations

import logging
from typing import Protocol

from furhat_demos.facevis.content import FACEVIS_INTRO

logger = logging.getLogger(__name__)


class DemoController(Protocol):
    def start_demo(self, demo_id: str, option_id: str) -> None: ...
    def set_face(self, face_id: str | None) -> None: ...
    def say(self, text: str) -> None: ...


class LoggingDemoController:
    def start_demo(self, demo_id: str, option_id: str) -> None:
        logger.info("start_demo requested: demo_id=%s option_id=%s", demo_id, option_id)

    def set_face(self, face_id: str | None) -> None:
        logger.info("set_face requested: face_id=%s", face_id)

    def say(self, text: str) -> None:
        logger.info("say requested: text=%s", text)


class FurhatRealtimeClient(Protocol):
    """The subset of furhat_realtime_api.FurhatClient this project uses."""

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def request_speak_text(self, text: str, wait: bool = True) -> None: ...
    def request_voice_config(self, **kwargs: object) -> object: ...
    def request_attend_user(self) -> object: ...
    def request_face_config(
        self, face_id: str | None, visibility: bool, microexpressions: bool
    ) -> object: ...
    def request_face_reset(self) -> object: ...


# Spoken intros, keyed by (demo_id, option_id).
_INTROS: dict[tuple[str, str], str] = {
    ("facevis", "air-quality"): FACEVIS_INTRO,
}

_DEFAULT_INTRO = "Hi! Let's get started."


class FurhatDemoController:
    def __init__(self, client: FurhatRealtimeClient) -> None:
        self._client = client
        self._voice_ensured = False

    def _ensure_english_voice(self) -> None:
        if self._voice_ensured:
            return
        self._voice_ensured = True
        try:
            self._client.request_voice_config(language="en-US")
        except Exception:
            logger.warning(
                "Failed to set an English voice on Furhat; continuing anyway", exc_info=True
            )

    def _ensure_attending_user(self) -> None:
        try:
            self._client.request_attend_user()
        except Exception:
            logger.warning("Failed to attend to a user on Furhat; continuing anyway", exc_info=True)

    def start_demo(self, demo_id: str, option_id: str) -> None:
        self._ensure_english_voice()
        self._ensure_attending_user()
        text = _INTROS.get((demo_id, option_id), _DEFAULT_INTRO)
        self._client.request_speak_text(text, wait=False)

    def set_face(self, face_id: str | None) -> None:
        try:
            if face_id is None:
                self._client.request_face_reset()
            else:
                self._client.request_face_config(
                    face_id=face_id, visibility=True, microexpressions=True
                )
        except Exception:
            logger.warning("Failed to set face on Furhat; continuing anyway", exc_info=True)

    def say(self, text: str) -> None:
        try:
            self._client.request_speak_text(text, wait=False)
        except Exception:
            logger.warning("Failed to speak on Furhat; continuing anyway", exc_info=True)
