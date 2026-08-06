from furhat_demos.config import FURHAT_HOST_ENV_VAR, OPENAI_API_KEY_ENV_VAR, build_controller
from furhat_demos.control import FurhatDemoController, LoggingDemoController
from furhat_demos.opendemo.llm_client import OpenAIChatClient


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
    monkeypatch.delenv(OPENAI_API_KEY_ENV_VAR, raising=False)

    controller = build_controller()

    assert isinstance(controller, FurhatDemoController)
    assert controller._llm_client is None


def test_build_controller_wires_llm_client_when_openai_api_key_set(monkeypatch):
    monkeypatch.setenv(FURHAT_HOST_ENV_VAR, "localhost")
    monkeypatch.setenv(OPENAI_API_KEY_ENV_VAR, "test-key")

    controller = build_controller()

    assert isinstance(controller, FurhatDemoController)
    assert isinstance(controller._llm_client, OpenAIChatClient)
