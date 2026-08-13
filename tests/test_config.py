from furhat_demos.config import OPENAI_API_KEY_ENV_VAR, build_llm_client
from furhat_demos.opendemo.llm_client import OpenAIChatClient


def test_build_llm_client_returns_none_when_unset(monkeypatch):
    monkeypatch.delenv(OPENAI_API_KEY_ENV_VAR, raising=False)

    assert build_llm_client() is None


def test_build_llm_client_returns_none_when_blank(monkeypatch):
    monkeypatch.setenv(OPENAI_API_KEY_ENV_VAR, "")

    assert build_llm_client() is None


def test_build_llm_client_returns_openai_chat_client_when_set(monkeypatch):
    monkeypatch.setenv(OPENAI_API_KEY_ENV_VAR, "test-key")

    client = build_llm_client()

    assert isinstance(client, OpenAIChatClient)
