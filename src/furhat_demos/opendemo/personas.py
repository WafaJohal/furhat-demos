from __future__ import annotations

from furhat_demos.opendemo.llm_client import LLMClient
from furhat_demos.opendemo.qa import DATA_DIR, QAEngine, load_chunks

PERSONA_DATA_DIR = DATA_DIR / "personas"

GUIDE_SYSTEM_PROMPT = (
    "You are Furhat, an Open Day guide for the University of Melbourne's School of "
    "Computing and Information Systems. Answer the visitor's question using ONLY the "
    "context provided below. Keep answers short and conversational, suitable for being "
    "spoken aloud. Do not use information beyond the given context."
)

WAFA_JOHAL_SYSTEM_PROMPT = (
    "You are Furhat, speaking as a persona representing Wafa Johal, a researcher at the "
    "University of Melbourne's School of Computing and Information Systems. Answer the "
    "visitor's question using ONLY the context provided below, speaking in first person "
    "where the context is about your own research. Keep answers short and conversational, "
    "suitable for being spoken aloud. Do not use information beyond the given context."
)

_SYSTEM_PROMPTS: dict[str, str] = {
    "guide": GUIDE_SYSTEM_PROMPT,
    "wafa-johal": WAFA_JOHAL_SYSTEM_PROMPT,
}


def build_qa_engine(persona_id: str, llm_client: LLMClient) -> QAEngine:
    chunks = load_chunks(DATA_DIR)
    if persona_id == "wafa-johal":
        chunks = chunks + load_chunks(PERSONA_DATA_DIR)
    system_prompt = _SYSTEM_PROMPTS.get(persona_id, GUIDE_SYSTEM_PROMPT)
    return QAEngine(llm_client, chunks=chunks, system_prompt=system_prompt)
