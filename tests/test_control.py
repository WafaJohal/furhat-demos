import logging

from furhat_demos.control import LoggingDemoController


def test_logging_demo_controller_logs(caplog):
    controller = LoggingDemoController()
    with caplog.at_level(logging.INFO):
        controller.start_demo("opendemo", "guide")
    assert "opendemo" in caplog.text
    assert "guide" in caplog.text
