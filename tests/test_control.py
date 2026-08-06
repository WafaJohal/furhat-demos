import logging
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

from furhat_demos.control import FurhatDemoController, LoggingDemoController


def test_logging_demo_controller_logs(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.start_demo("opendemo", "guide")
    assert "opendemo" in caplog.text
    assert "guide" in caplog.text


@dataclass
class FakeVoice:
    name: str
    language: str | None


@dataclass
class FakeListenResult:
    message: str | None


@dataclass
class FakeRemoteApi:
    voices: list[FakeVoice] = field(default_factory=list)
    calls: list[dict] = field(default_factory=list)
    set_voice_calls: list[str] = field(default_factory=list)
    voices_error: Exception | None = None
    listen_result: FakeListenResult | None = None
    listen_call_count: int = 0

    def say(self, **kwargs):
        self.calls.append(kwargs)

    def get_voices(self):
        if self.voices_error is not None:
            raise self.voices_error
        return self.voices

    def set_voice(self, name):
        self.set_voice_calls.append(name)

    def listen(self):
        self.listen_call_count += 1
        return self.listen_result


class FakeLLMClient:
    def chat(self, *, system, user):
        raise AssertionError("FakeLLMClient.chat should not be called directly in these tests")


def test_furhat_demo_controller_says_known_intro():
    fake = FakeRemoteApi()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")

    assert len(fake.calls) == 1
    assert "Open Day" in fake.calls[0]["text"]
    assert fake.calls[0]["blocking"] is False


def test_furhat_demo_controller_known_combos_have_distinct_intros():
    fake = FakeRemoteApi()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "wafa-johal")
    controller.start_demo("facevis", "air-quality")

    texts = [call["text"] for call in fake.calls]
    assert len(texts) == len(set(texts))
    assert "Wafa Johal" in texts[0]
    assert "air quality" in texts[1]


def test_furhat_demo_controller_falls_back_for_unknown_combo():
    fake = FakeRemoteApi()
    controller = FurhatDemoController(fake)

    controller.start_demo("unknown-demo", "unknown-option")

    assert len(fake.calls) == 1
    assert fake.calls[0]["text"]


def test_furhat_demo_controller_selects_english_voice():
    fake = FakeRemoteApi(voices=[FakeVoice("Ines", "es-ES"), FakeVoice("William", "en-US")])
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")

    assert fake.set_voice_calls == ["William"]
    assert len(fake.calls) == 1


def test_furhat_demo_controller_only_selects_voice_once():
    fake = FakeRemoteApi(voices=[FakeVoice("William", "en-US")])
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")
    controller.start_demo("facevis", "air-quality")

    assert fake.set_voice_calls == ["William"]
    assert len(fake.calls) == 2


def test_furhat_demo_controller_warns_and_continues_when_no_english_voice(caplog):
    fake = FakeRemoteApi(voices=[FakeVoice("Ines", "es-ES")])
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("opendemo", "guide")

    assert fake.set_voice_calls == []
    assert len(fake.calls) == 1
    assert "No English voice" in caplog.text


def test_furhat_demo_controller_warns_and_continues_when_voice_lookup_fails(caplog):
    fake = FakeRemoteApi(voices_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("opendemo", "guide")

    assert fake.set_voice_calls == []
    assert len(fake.calls) == 1
    assert "Failed to set an English voice" in caplog.text


def test_furhat_demo_controller_runs_qa_turn_after_intro_when_llm_client_set():
    fake = FakeRemoteApi(listen_result=FakeListenResult(message="What is COMP10001?"))
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.return_value = "It's an intro programming subject."

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine) as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_called_once_with("guide", llm)
    fake_engine.answer.assert_called_once_with("What is COMP10001?")
    assert fake.listen_call_count == 1
    assert len(fake.calls) == 2
    assert fake.calls[0]["blocking"] is True  # intro blocks so listen() doesn't hear itself
    assert fake.calls[1] == {"text": "It's an intro programming subject.", "blocking": False}


def test_furhat_demo_controller_skips_qa_turn_without_llm_client():
    fake = FakeRemoteApi(listen_result=FakeListenResult(message="What is COMP10001?"))
    controller = FurhatDemoController(fake)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["blocking"] is False


def test_furhat_demo_controller_skips_qa_turn_for_non_opendemo():
    fake = FakeRemoteApi(listen_result=FakeListenResult(message="irrelevant"))
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("facevis", "air-quality")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["blocking"] is False


def test_furhat_demo_controller_speaks_fallback_when_no_question_heard():
    fake = FakeRemoteApi(listen_result=FakeListenResult(message="SILENCE"))
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_not_called()
    assert len(fake.calls) == 2
    assert "didn't catch a question" in fake.calls[1]["text"]
    assert fake.calls[1]["blocking"] is False


def test_furhat_demo_controller_speaks_fallback_when_listen_returns_none_message():
    fake = FakeRemoteApi(listen_result=FakeListenResult(message=None))
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_not_called()
    assert len(fake.calls) == 2
    assert "didn't catch a question" in fake.calls[1]["text"]
