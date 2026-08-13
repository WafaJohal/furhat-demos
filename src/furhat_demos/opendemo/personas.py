from __future__ import annotations

from furhat_demos.opendemo.llm_client import LLMClient
from furhat_demos.opendemo.qa import DATA_DIR, QAEngine, load_chunks

GUIDE_SYSTEM_PROMPT = (
    "You are Furhat, an Open Day guide for the University of Melbourne's School of "
    "Computing and Information Systems. Answer the visitor's question using ONLY the "
    "context provided below. Keep answers short and conversational, suitable for being "
    "spoken aloud. Do not use information beyond the given context."
)


def build_qa_engine(persona_id: str, llm_client: LLMClient) -> QAEngine:
    # persona_id is unused now that only "guide" remains, but kept in the
    # signature so callers don't change if/when persona-specific content
    # returns (see BACKLOG.md).
    return QAEngine(llm_client, chunks=load_chunks(DATA_DIR), system_prompt=GUIDE_SYSTEM_PROMPT)
