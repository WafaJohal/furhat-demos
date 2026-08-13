from furhat_demos.opendemo.personas import GUIDE_SYSTEM_PROMPT, build_qa_engine


class FakeLLMClient:
    def __init__(self, response: str = "fake answer"):
        self.response = response
        self.calls: list[dict] = []

    def chat(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.response


def test_guide_persona_uses_guide_system_prompt_and_handbook_content():
    llm = FakeLLMClient()
    engine = build_qa_engine("guide", llm)

    engine.answer("What is Foundations of Computing?")

    assert len(llm.calls) == 1
    assert llm.calls[0]["system"] == GUIDE_SYSTEM_PROMPT
    assert "Foundations of Computing" in llm.calls[0]["user"]


def test_unknown_option_still_uses_guide_system_prompt_and_content():
    llm = FakeLLMClient()
    engine = build_qa_engine("some-unknown-option", llm)

    engine.answer("What is Foundations of Computing?")

    assert len(llm.calls) == 1
    assert llm.calls[0]["system"] == GUIDE_SYSTEM_PROMPT
    assert "Foundations of Computing" in llm.calls[0]["user"]
