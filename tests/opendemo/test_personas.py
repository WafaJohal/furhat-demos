from furhat_demos.opendemo.personas import (
    GUIDE_SYSTEM_PROMPT,
    WAFA_JOHAL_SYSTEM_PROMPT,
    build_qa_engine,
)


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


def test_guide_persona_has_no_wafa_johal_bio_content():
    llm = FakeLLMClient()
    engine = build_qa_engine("guide", llm)

    engine.answer("Tell me about Wafa Johal's research group")

    # The guide persona isn't given the Wafa Johal bio doc, so this should be
    # treated as ungrounded rather than answered from it.
    assert llm.calls == []


def test_wafa_johal_persona_uses_her_system_prompt_and_bio_content():
    llm = FakeLLMClient()
    engine = build_qa_engine("wafa-johal", llm)

    engine.answer("Tell me about your research group")

    assert len(llm.calls) == 1
    assert llm.calls[0]["system"] == WAFA_JOHAL_SYSTEM_PROMPT
    assert "research" in llm.calls[0]["user"].lower()


def test_wafa_johal_persona_can_also_answer_general_handbook_questions():
    llm = FakeLLMClient()
    engine = build_qa_engine("wafa-johal", llm)

    engine.answer("What is Foundations of Computing?")

    assert len(llm.calls) == 1
    assert "Foundations of Computing" in llm.calls[0]["user"]


def test_unknown_persona_falls_back_to_guide_system_prompt():
    llm = FakeLLMClient()
    engine = build_qa_engine("some-unknown-persona", llm)

    engine.answer("What is Foundations of Computing?")

    assert len(llm.calls) == 1
    assert llm.calls[0]["system"] == GUIDE_SYSTEM_PROMPT
