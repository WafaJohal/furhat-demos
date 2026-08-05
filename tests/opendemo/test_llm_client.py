from unittest.mock import MagicMock, patch

from furhat_demos.opendemo.llm_client import OpenAIChatClient


def test_openai_chat_client_calls_chat_completions_and_returns_text():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="Hello there!"))]

    fake_openai_instance = MagicMock()
    fake_openai_instance.chat.completions.create.return_value = fake_response

    with patch("openai.OpenAI", return_value=fake_openai_instance) as mock_openai_cls:
        client = OpenAIChatClient(api_key="test-key")
        result = client.chat(system="be helpful", user="hi")

    mock_openai_cls.assert_called_once_with(api_key="test-key")
    fake_openai_instance.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "be helpful"},
            {"role": "user", "content": "hi"},
        ],
    )
    assert result == "Hello there!"


def test_openai_chat_client_returns_empty_string_when_content_is_none():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content=None))]

    fake_openai_instance = MagicMock()
    fake_openai_instance.chat.completions.create.return_value = fake_response

    with patch("openai.OpenAI", return_value=fake_openai_instance):
        client = OpenAIChatClient(api_key="test-key")
        result = client.chat(system="be helpful", user="hi")

    assert result == ""
