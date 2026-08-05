import logging

from furhat_demos.control import FurhatDemoController, LoggingDemoController


def test_logging_demo_controller_logs(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.start_demo("opendemo", "guide")
    assert "opendemo" in caplog.text
    assert "guide" in caplog.text


class FakeRemoteApi:
    def __init__(self):
        self.calls: list[dict] = []

    def say(self, **kwargs):
        self.calls.append(kwargs)


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
