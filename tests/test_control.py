import logging
from dataclasses import dataclass, field

from furhat_demos.control import FurhatDemoController, LoggingDemoController


def test_logging_demo_controller_logs(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.start_demo("facevis", "air-quality")
    assert "facevis" in caplog.text
    assert "air-quality" in caplog.text


def test_logging_demo_controller_logs_set_face(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.set_face("AirHazard/AirHazard3")
    assert "AirHazard/AirHazard3" in caplog.text


def test_logging_demo_controller_logs_say(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.say("The air quality in Delhi is hazardous.")
    assert "The air quality in Delhi is hazardous." in caplog.text


@dataclass
class FakeRealtimeClient:
    calls: list[dict] = field(default_factory=list)
    voice_config_calls: list[dict] = field(default_factory=list)
    attend_user_calls: int = 0
    voice_config_error: Exception | None = None
    attend_user_error: Exception | None = None
    face_config_calls: list[dict] = field(default_factory=list)
    face_reset_calls: int = 0
    face_config_error: Exception | None = None
    face_reset_error: Exception | None = None
    speak_error: Exception | None = None

    def request_speak_text(self, text, wait=True):
        if self.speak_error is not None:
            raise self.speak_error
        self.calls.append({"text": text, "wait": wait})

    def request_voice_config(self, **kwargs):
        if self.voice_config_error is not None:
            raise self.voice_config_error
        self.voice_config_calls.append(kwargs)

    def request_attend_user(self):
        self.attend_user_calls += 1
        if self.attend_user_error is not None:
            raise self.attend_user_error

    def request_face_config(self, face_id, visibility, microexpressions):
        if self.face_config_error is not None:
            raise self.face_config_error
        self.face_config_calls.append(
            {"face_id": face_id, "visibility": visibility, "microexpressions": microexpressions}
        )

    def request_face_reset(self):
        self.face_reset_calls += 1
        if self.face_reset_error is not None:
            raise self.face_reset_error


def test_furhat_demo_controller_says_known_intro():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("facevis", "air-quality")

    assert len(fake.calls) == 1
    assert "air quality" in fake.calls[0]["text"]
    assert fake.calls[0]["wait"] is False


def test_furhat_demo_controller_falls_back_for_unknown_combo():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("unknown-demo", "unknown-option")

    assert len(fake.calls) == 1
    assert fake.calls[0]["text"]


def test_furhat_demo_controller_selects_english_voice_once():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("facevis", "air-quality")
    controller.start_demo("facevis", "air-quality")

    assert fake.voice_config_calls == [{"language": "en-US"}]
    assert len(fake.calls) == 2


def test_furhat_demo_controller_attends_a_user_on_every_start():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("facevis", "air-quality")
    controller.start_demo("facevis", "air-quality")

    assert fake.attend_user_calls == 2


def test_furhat_demo_controller_warns_and_continues_when_voice_config_fails(caplog):
    fake = FakeRealtimeClient(voice_config_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("facevis", "air-quality")

    assert len(fake.calls) == 1
    assert "Failed to set an English voice" in caplog.text


def test_furhat_demo_controller_warns_and_continues_when_attend_user_fails(caplog):
    fake = FakeRealtimeClient(attend_user_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("facevis", "air-quality")

    assert len(fake.calls) == 1
    assert "Failed to attend to a user" in caplog.text


def test_furhat_demo_controller_set_face_with_face_id():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.set_face("AirHazard/AirHazard3")

    assert fake.face_config_calls == [
        {"face_id": "AirHazard/AirHazard3", "visibility": True, "microexpressions": True}
    ]
    assert fake.face_reset_calls == 0


def test_furhat_demo_controller_set_face_none_resets_face():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.set_face(None)

    assert fake.face_reset_calls == 1
    assert fake.face_config_calls == []


def test_furhat_demo_controller_set_face_warns_and_continues_on_failure(caplog):
    fake = FakeRealtimeClient(face_config_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.set_face("AirHazard/AirHazard3")

    assert "Failed to set face" in caplog.text


def test_furhat_demo_controller_set_face_reset_warns_and_continues_on_failure(caplog):
    fake = FakeRealtimeClient(face_reset_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.set_face(None)

    assert "Failed to set face" in caplog.text


def test_furhat_demo_controller_say_speaks_without_waiting():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.say("The air quality in Delhi is hazardous.")

    assert fake.calls == [{"text": "The air quality in Delhi is hazardous.", "wait": False}]


def test_furhat_demo_controller_say_warns_and_continues_on_failure(caplog):
    fake = FakeRealtimeClient(speak_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.say("The air quality in Delhi is hazardous.")

    assert "Failed to speak" in caplog.text
