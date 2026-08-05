from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from furhat_demos.opendemo.llm_client import LLMClient

DATA_DIR = Path(__file__).resolve().parent / "data"

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_WORD_RE = re.compile(r"[a-zA-Z']+")

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "what", "which", "who", "whom", "how", "why", "when", "where",
    "i", "you", "it", "this", "that", "of", "in", "on", "for", "to",
    "and", "or", "with", "about", "at", "as", "be", "can", "could",
}  # fmt: skip

_SYSTEM_PROMPT = (
    "You are Furhat, an Open Day guide for the University of Melbourne's School of "
    "Computing and Information Systems. Answer the visitor's question using ONLY the "
    "context provided below. Keep answers short and conversational, suitable for being "
    "spoken aloud. Do not use information beyond the given context."
)

NO_MATCH_ANSWER = (
    "I'm not sure about that one — it's outside what I've been given to talk about. "
    "A staff member at the Open Day info desk should be able to help."
)


def _tokenize(text: str) -> set[str]:
    return {w for w in (m.lower() for m in _WORD_RE.findall(text)) if w not in _STOPWORDS}


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


def load_chunks(data_dir: Path = DATA_DIR) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(data_dir.glob("*.md")):
        text = _COMMENT_RE.sub("", path.read_text())
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks.extend(Chunk(source=path.name, text=p) for p in paragraphs)
    return chunks


class QAEngine:
    def __init__(
        self,
        llm_client: LLMClient,
        chunks: list[Chunk] | None = None,
        top_k: int = 3,
    ) -> None:
        self._llm_client = llm_client
        self._chunks = chunks if chunks is not None else load_chunks()
        self._top_k = top_k

    def _retrieve(self, question: str) -> list[Chunk]:
        question_words = _tokenize(question)
        if not question_words:
            return []
        scored = [(len(question_words & _tokenize(chunk.text)), chunk) for chunk in self._chunks]
        scored = [(score, chunk) for score, chunk in scored if score > 0]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[: self._top_k]]

    def answer(self, question: str) -> str:
        relevant = self._retrieve(question)
        if not relevant:
            return NO_MATCH_ANSWER
        context = "\n\n".join(chunk.text for chunk in relevant)
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
        return self._llm_client.chat(system=_SYSTEM_PROMPT, user=user_prompt)
