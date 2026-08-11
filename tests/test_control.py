import logging
from dataclasses import dataclass, field
from unittest.mock import MagicMock, call, patch

from furhat_demos.control import _MAX_QA_TURNS, FurhatDemoController, LoggingDemoController


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
    listen_results: list[FakeListenResult] = field(default_factory=list)
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
        if self.listen_call_count <= len(self.listen_results):
            return self.listen_results[self.listen_call_count - 1]
        return FakeListenResult(message="SILENCE")


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


def test_furhat_demo_controller_skips_qa_turn_without_llm_client():
    fake = FakeRemoteApi(listen_results=[FakeListenResult(message="What is COMP10001?")])
    controller = FurhatDemoController(fake)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["blocking"] is False


def test_furhat_demo_controller_skips_qa_turn_for_non_opendemo():
    fake = FakeRemoteApi(listen_results=[FakeListenResult(message="irrelevant")])
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("facevis", "air-quality")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["blocking"] is False


def test_furhat_demo_controller_answers_then_exits_on_exit_phrase():
    fake = FakeRemoteApi(
        listen_results=[
            FakeListenResult(message="What is COMP10001?"),
            FakeListenResult(message="bye"),
        ]
    )
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.return_value = "It's an intro programming subject."

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine) as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_called_once_with("guide", llm)
    fake_engine.answer.assert_called_once_with("What is COMP10001?")
    assert fake.listen_call_count == 2
    assert len(fake.calls) == 3
    assert fake.calls[0]["blocking"] is True  # intro blocks so listen() doesn't hear itself
    assert fake.calls[1] == {"text": "It's an intro programming subject.", "blocking": True}
    assert "Thanks for chatting" in fake.calls[2]["text"]
    assert fake.calls[2]["blocking"] is False


def test_furhat_demo_controller_answers_multiple_questions_in_one_loop():
    fake = FakeRemoteApi(
        listen_results=[
            FakeListenResult(message="question one"),
            FakeListenResult(message="question two"),
            FakeListenResult(message="goodbye"),
        ]
    )
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.side_effect = ["answer one", "answer two"]

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine):
        controller.start_demo("opendemo", "guide")

    assert fake_engine.answer.call_args_list == [call("question one"), call("question two")]
    spoken_texts = [c["text"] for c in fake.calls]
    assert "answer one" in spoken_texts
    assert "answer two" in spoken_texts
    assert "Thanks for chatting" in spoken_texts[-1]


def test_furhat_demo_controller_nudges_once_on_single_silence_then_continues():
    fake = FakeRemoteApi(
        listen_results=[
            FakeListenResult(message="SILENCE"),
            FakeListenResult(message="a real question"),
            FakeListenResult(message="bye"),
        ]
    )
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.return_value = "an answer"

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine):
        controller.start_demo("opendemo", "guide")

    spoken_texts = [c["text"] for c in fake.calls]
    assert sum("didn't catch a question" in t for t in spoken_texts) == 1
    assert "an answer" in spoken_texts
    assert fake.listen_call_count == 3


def test_furhat_demo_controller_ends_loop_after_two_consecutive_silences():
    fake = FakeRemoteApi(
        listen_results=[
            FakeListenResult(message="SILENCE"),
            FakeListenResult(message="SILENCE"),
        ]
    )
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine"):
        controller.start_demo("opendemo", "guide")

    assert fake.listen_call_count == 2
    spoken_texts = [c["text"] for c in fake.calls]
    assert sum("didn't catch a question" in t for t in spoken_texts) == 1
    assert "Thanks for chatting" in spoken_texts[-1]


def test_furhat_demo_controller_stops_after_max_turns():
    fake = FakeRemoteApi(
        listen_results=[FakeListenResult(message=f"question {i}") for i in range(_MAX_QA_TURNS + 5)]
    )
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.return_value = "an answer"

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine):
        controller.start_demo("opendemo", "guide")

    assert fake.listen_call_count == _MAX_QA_TURNS
    assert fake_engine.answer.call_count == _MAX_QA_TURNS
    assert "Thanks for chatting" in fake.calls[-1]["text"]
