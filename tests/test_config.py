from furhat_demos.config import FURHAT_HOST_ENV_VAR, build_controller
from furhat_demos.control import FurhatDemoController, LoggingDemoController


def test_build_controller_defaults_to_logging_when_unset(monkeypatch):
    monkeypatch.delenv(FURHAT_HOST_ENV_VAR, raising=False)

    controller = build_controller()

    assert isinstance(controller, LoggingDemoController)


def test_build_controller_defaults_to_logging_when_blank(monkeypatch):
    monkeypatch.setenv(FURHAT_HOST_ENV_VAR, "")

    controller = build_controller()

    assert isinstance(controller, LoggingDemoController)


def test_build_controller_uses_furhat_when_host_set(monkeypatch):
    monkeypatch.setenv(FURHAT_HOST_ENV_VAR, "localhost")

    controller = build_controller()

    assert isinstance(controller, FurhatDemoController)
