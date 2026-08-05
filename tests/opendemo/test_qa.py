from furhat_demos.opendemo.qa import NO_MATCH_ANSWER, Chunk, QAEngine, load_chunks


class FakeLLMClient:
    def __init__(self, response: str = "fake answer"):
        self.response = response
        self.calls: list[dict] = []

    def chat(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.response


SAMPLE_CHUNKS = [
    Chunk(
        source="courses.md",
        text=(
            "The Bachelor of Science majoring in Computing covers software "
            "engineering, AI, and data science."
        ),
    ),
    Chunk(
        source="teaching.md",
        text=(
            "Our teaching approach emphasises project-based learning and "
            "industry capstone projects."
        ),
    ),
]


def test_answer_uses_llm_when_relevant_context_found():
    fake = FakeLLMClient(response="We teach through project-based learning.")
    engine = QAEngine(fake, chunks=SAMPLE_CHUNKS)

    answer = engine.answer("What is your teaching approach?")

    assert answer == "We teach through project-based learning."
    assert len(fake.calls) == 1
    assert "project-based learning" in fake.calls[0]["user"]
    assert "ONLY the" in fake.calls[0]["system"]


def test_answer_returns_no_match_without_calling_llm_when_no_overlap():
    fake = FakeLLMClient()
    engine = QAEngine(fake, chunks=SAMPLE_CHUNKS)

    answer = engine.answer("What's the weather like on Mars?")

    assert answer == NO_MATCH_ANSWER
    assert fake.calls == []


def test_answer_handles_question_with_no_meaningful_words():
    fake = FakeLLMClient()
    engine = QAEngine(fake, chunks=SAMPLE_CHUNKS)

    answer = engine.answer("???")

    assert answer == NO_MATCH_ANSWER
    assert fake.calls == []


def test_retrieval_ranks_more_relevant_chunk_first():
    fake = FakeLLMClient()
    engine = QAEngine(fake, chunks=SAMPLE_CHUNKS, top_k=1)

    engine.answer("Tell me about your project-based teaching approach")

    assert len(fake.calls) == 1
    assert "project-based learning" in fake.calls[0]["user"]
    assert "Bachelor of Science" not in fake.calls[0]["user"]


def test_load_chunks_reads_placeholder_data_files_and_strips_comments():
    chunks = load_chunks()

    assert len(chunks) > 0
    assert all(chunk.text for chunk in chunks)
    assert all("<!--" not in chunk.text for chunk in chunks)
