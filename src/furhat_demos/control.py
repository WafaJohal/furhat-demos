from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class DemoController(Protocol):
    def start_demo(self, demo_id: str, option_id: str) -> None: ...


class LoggingDemoController:
    def start_demo(self, demo_id: str, option_id: str) -> None:
        logger.info("start_demo requested: demo_id=%s option_id=%s", demo_id, option_id)


class VoiceLike(Protocol):
    name: str
    language: str | None


class RemoteApi(Protocol):
    def say(self, **kwargs: object) -> object: ...
    def get_voices(self) -> list[VoiceLike]: ...
    def set_voice(self, name: str) -> object: ...


# Placeholder spoken intros — replaced by real RAG/persona logic (Demo 1) and
# FaceVis logic (Demo 2) in later cycles. Keyed by (demo_id, option_id).
_INTROS: dict[tuple[str, str], str] = {
    ("opendemo", "guide"): (
        "Hi! I'm Furhat, here to help with Open Day questions about our courses and curriculum."
    ),
    ("opendemo", "wafa-johal"): (
        "Hello, I'm a persona of Wafa Johal, here to tell you about my research group's work."
    ),
    ("facevis", "air-quality"): (
        "Watch my face as I visualize live air quality data from Melbourne and Victoria."
    ),
}

_DEFAULT_INTRO = "Hi! Let's get started."


class FurhatDemoController:
    def __init__(self, remote_api: RemoteApi) -> None:
        self._remote_api = remote_api
        self._voice_ensured = False

    def _ensure_english_voice(self) -> None:
        if self._voice_ensured:
            return
        self._voice_ensured = True
        try:
            voices = self._remote_api.get_voices()
            english_voice = next(
                (v for v in voices if v.language and v.language.lower().startswith("en")),
                None,
            )
            if english_voice is None:
                logger.warning("No English voice found on connected Furhat; leaving voice as-is")
                return
            self._remote_api.set_voice(name=english_voice.name)
        except Exception:
            logger.warning(
                "Failed to set an English voice on Furhat; continuing anyway", exc_info=True
            )

    def start_demo(self, demo_id: str, option_id: str) -> None:
        self._ensure_english_voice()
        text = _INTROS.get((demo_id, option_id), _DEFAULT_INTRO)
        self._remote_api.say(text=text, blocking=False)
