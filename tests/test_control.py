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


def test_logging_demo_controller_logs_set_face(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.set_face("AirHazard/AirHazard3")
    assert "AirHazard/AirHazard3" in caplog.text


@dataclass
class FakeRealtimeClient:
    calls: list[dict] = field(default_factory=list)
    voice_config_calls: list[dict] = field(default_factory=list)
    attend_user_calls: int = 0
    voice_config_error: Exception | None = None
    attend_user_error: Exception | None = None
    listen_results: list[str] = field(default_factory=list)
    listen_call_count: int = 0
    face_config_calls: list[dict] = field(default_factory=list)
    face_reset_calls: int = 0
    face_config_error: Exception | None = None
    face_reset_error: Exception | None = None

    def request_speak_text(self, text, wait=True):
        self.calls.append({"text": text, "wait": wait})

    def request_voice_config(self, **kwargs):
        if self.voice_config_error is not None:
            raise self.voice_config_error
        self.voice_config_calls.append(kwargs)

    def request_attend_user(self):
        self.attend_user_calls += 1
        if self.attend_user_error is not None:
            raise self.attend_user_error

    def request_listen_start(self, **kwargs):
        self.listen_call_count += 1
        if self.listen_call_count <= len(self.listen_results):
            return self.listen_results[self.listen_call_count - 1]
        return ""

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


class FakeLLMClient:
    def chat(self, *, system, user):
        raise AssertionError("FakeLLMClient.chat should not be called directly in these tests")


def test_furhat_demo_controller_says_known_intro():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")

    assert len(fake.calls) == 1
    assert "Open Day" in fake.calls[0]["text"]
    assert fake.calls[0]["wait"] is False


def test_furhat_demo_controller_known_combos_have_distinct_intros():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")
    controller.start_demo("facevis", "air-quality")

    texts = [c["text"] for c in fake.calls]
    assert len(texts) == len(set(texts))
    assert "Open Day" in texts[0]
    assert "air quality" in texts[1]


def test_furhat_demo_controller_falls_back_for_unknown_combo():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("unknown-demo", "unknown-option")

    assert len(fake.calls) == 1
    assert fake.calls[0]["text"]


def test_furhat_demo_controller_selects_english_voice_once():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")
    controller.start_demo("facevis", "air-quality")

    assert fake.voice_config_calls == [{"language": "en-US"}]
    assert len(fake.calls) == 2


def test_furhat_demo_controller_attends_a_user_on_every_start():
    fake = FakeRealtimeClient()
    controller = FurhatDemoController(fake)

    controller.start_demo("opendemo", "guide")
    controller.start_demo("facevis", "air-quality")

    assert fake.attend_user_calls == 2


def test_furhat_demo_controller_warns_and_continues_when_voice_config_fails(caplog):
    fake = FakeRealtimeClient(voice_config_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("opendemo", "guide")

    assert len(fake.calls) == 1
    assert "Failed to set an English voice" in caplog.text


def test_furhat_demo_controller_warns_and_continues_when_attend_user_fails(caplog):
    fake = FakeRealtimeClient(attend_user_error=RuntimeError("robot unreachable"))
    controller = FurhatDemoController(fake)

    with caplog.at_level(logging.WARNING):
        controller.start_demo("opendemo", "guide")

    assert len(fake.calls) == 1
    assert "Failed to attend to a user" in caplog.text


def test_furhat_demo_controller_skips_qa_turn_without_llm_client():
    fake = FakeRealtimeClient(listen_results=["What is COMP10001?"])
    controller = FurhatDemoController(fake)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("opendemo", "guide")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["wait"] is False


def test_furhat_demo_controller_skips_qa_turn_for_non_opendemo():
    fake = FakeRealtimeClient(listen_results=["irrelevant"])
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine") as mock_build:
        controller.start_demo("facevis", "air-quality")

    mock_build.assert_not_called()
    assert fake.listen_call_count == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["wait"] is False


def test_furhat_demo_controller_answers_then_exits_on_exit_phrase():
    fake = FakeRealtimeClient(listen_results=["What is COMP10001?", "bye"])
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
    assert fake.calls[0]["wait"] is True  # intro waits so listen() doesn't hear itself
    assert fake.calls[1] == {"text": "It's an intro programming subject.", "wait": True}
    assert "Thanks for chatting" in fake.calls[2]["text"]
    assert fake.calls[2]["wait"] is False


def test_furhat_demo_controller_answers_multiple_questions_in_one_loop():
    fake = FakeRealtimeClient(listen_results=["question one", "question two", "goodbye"])
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
    fake = FakeRealtimeClient(listen_results=["", "a real question", "bye"])
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
    fake = FakeRealtimeClient(listen_results=["", ""])
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    with patch("furhat_demos.control.build_qa_engine"):
        controller.start_demo("opendemo", "guide")

    assert fake.listen_call_count == 2
    spoken_texts = [c["text"] for c in fake.calls]
    assert sum("didn't catch a question" in t for t in spoken_texts) == 1
    assert "Thanks for chatting" in spoken_texts[-1]


def test_furhat_demo_controller_stops_after_max_turns():
    fake = FakeRealtimeClient(listen_results=[f"question {i}" for i in range(_MAX_QA_TURNS + 5)])
    llm = FakeLLMClient()
    controller = FurhatDemoController(fake, llm_client=llm)

    fake_engine = MagicMock()
    fake_engine.answer.return_value = "an answer"

    with patch("furhat_demos.control.build_qa_engine", return_value=fake_engine):
        controller.start_demo("opendemo", "guide")

    assert fake.listen_call_count == _MAX_QA_TURNS
    assert fake_engine.answer.call_count == _MAX_QA_TURNS
    assert "Thanks for chatting" in fake.calls[-1]["text"]


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
