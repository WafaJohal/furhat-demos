# ADR-003: Word-overlap retrieval (not embeddings) for the Demo 1 Q&A core

- **Status:** accepted
- **Date:** 2026-08-05
- **Cycle:** cycle-004

## Context

`QAEngine` needs to retrieve relevant document chunks for a visitor's question before asking the LLM to answer (and to decide when to skip the LLM entirely and say "I don't know"). Two realistic options: call an embeddings API (e.g. OpenAI embeddings) to do semantic similarity search, or use plain lexical/word-overlap scoring.

## Decision

We will use plain word-overlap scoring (tokenize, drop stopwords, count shared words between question and chunk) for this first cycle, with the LLM only called when at least one chunk has nonzero overlap.

## Alternatives considered

- **Embeddings-based semantic search** — better retrieval quality, robust to paraphrasing/vocabulary mismatch. Rejected *for this cycle* because it requires a real API call (and therefore either mocking an embeddings client in every retrieval test, or hitting the network), adds a vector-store dependency, and is more than needed to prove out the core "retrieve → ground → refuse if ungrounded" behavior first.
- **No retrieval gate, always call the LLM** — rejected: the user's explicit requirement is that the robot says "I don't know" rather than guessing; gating on retrieval gives that guarantee at the code level instead of relying entirely on the LLM following instructions.

## Consequences

- Fully offline-testable: no network/API key needed in CI for retrieval logic itself (only the real `OpenAIChatClient`, used for the answer step, needs a key — and it isn't exercised in CI either, just unit-tested against a mock).
- **Real, demonstrated limitation**: brittle to vocabulary mismatch. Confirmed during this cycle's manual smoke test — "What courses do you offer?" returned the fallback "I don't know" response because the placeholder document said "Bachelor of Science" / "Master of..." rather than the literal word "courses". Worked around for that one case by editing the placeholder doc, but the same failure mode will recur on real pamphlet content whenever a visitor's phrasing doesn't share literal words with the source text.
- Recorded as `ASSUMPTIONS.md` A-006 (invalidated for the general case) and a `BACKLOG.md` item to move to embeddings/semantic retrieval before this is trusted against real, unedited pamphlet content.
