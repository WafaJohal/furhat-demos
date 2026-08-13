from __future__ import annotations

import logging
from typing import Protocol

from furhat_demos.facevis.content import FACEVIS_INTRO
from furhat_demos.opendemo.llm_client import LLMClient
from furhat_demos.opendemo.personas import build_qa_engine

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
    def request_listen_start(self, **kwargs: object) -> str: ...
    def request_voice_config(self, **kwargs: object) -> object: ...
    def request_attend_user(self) -> object: ...
    def request_face_config(
        self, face_id: str | None, visibility: bool, microexpressions: bool
    ) -> object: ...
    def request_face_reset(self) -> object: ...


_MAX_QA_TURNS = 10

_EXIT_PHRASES = (
    "goodbye",
    "bye",
    "no more questions",
    "that's all",
    "i'm done",
    "stop asking",
)

_NO_QUESTION_HEARD = (
    "Sorry, I didn't catch a question there — feel free to come back and try again!"
)

_GOODBYE = "Thanks for chatting with me! Come back any time you have more questions."


def _is_exit_phrase(question: str) -> bool:
    lowered = question.lower()
    return any(phrase in lowered for phrase in _EXIT_PHRASES)


# Spoken intros, keyed by (demo_id, option_id).
_INTROS: dict[tuple[str, str], str] = {
    ("opendemo", "guide"): (
        "Hi! I'm Furhat, here to help with Open Day questions about our courses and curriculum."
    ),
    ("facevis", "air-quality"): FACEVIS_INTRO,
}

_DEFAULT_INTRO = "Hi! Let's get started."


class FurhatDemoController:
    def __init__(self, client: FurhatRealtimeClient, llm_client: LLMClient | None = None) -> None:
        self._client = client
        self._llm_client = llm_client
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
        will_run_qa_turn = demo_id == "opendemo" and self._llm_client is not None
        # Wait for the intro to finish when a QA turn follows, so listen()
        # doesn't pick up the tail of the robot's own intro speech.
        self._client.request_speak_text(text, wait=will_run_qa_turn)
        if will_run_qa_turn:
            self._run_qa_loop(option_id)

    def _run_qa_loop(self, option_id: str) -> None:
        engine = build_qa_engine(option_id, self._llm_client)
        consecutive_silences = 0
        for _ in range(_MAX_QA_TURNS):
            question = self._client.request_listen_start()
            if not question:
                consecutive_silences += 1
                if consecutive_silences >= 2:
                    break
                self._client.request_speak_text(_NO_QUESTION_HEARD, wait=True)
                continue
            consecutive_silences = 0
            if _is_exit_phrase(question):
                break
            answer = engine.answer(question)
            self._client.request_speak_text(answer, wait=True)
        self._client.request_speak_text(_GOODBYE, wait=False)

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
