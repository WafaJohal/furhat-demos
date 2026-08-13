# ADR-007: Exit conditions for the continuous opendemo Q&A loop

- **Status:** accepted
- **Date:** 2026-08-10
- **Cycle:** cycle-008

## Context

Cycle-006 shipped a single question-then-answer round per button press. This cycle replaces it with a loop so a visitor can ask several questions in one interaction. A loop needs well-defined exit conditions — otherwise a live demo risks either cutting a visitor off mid-conversation or getting stuck listening indefinitely (e.g. if nobody's there anymore, or `listen()` misbehaves).

## Decision

The loop ends, and a goodbye line is spoken, on whichever comes first:

1. **An exit phrase** in the recognized speech: `"goodbye"`, `"bye"`, `"no more questions"`, `"that's all"`, `"i'm done"`, `"stop asking"` (case-insensitive substring match). Checked *before* the text is sent to `QAEngine`, so an exit phrase is never treated as a question to answer.
2. **Two consecutive** `SILENCE`/`INTERRUPTED`/`FAILED`/empty `listen()` results. A *single* silence gets one spoken nudge ("didn't catch a question...") and the loop continues — people pause to think, and ending on the first silence would cut visitors off too eagerly.
3. **A hard cap of 10 turns**, regardless of what's being said, as a safety net against `listen()` behaving unexpectedly (e.g. always returning speech, never silence) in a live, unattended demo.

## Alternatives considered

- **End on any single silence** — rejected: too eager, likely to cut off a visitor who's just pausing to think of their next question.
- **No exit phrase detection, rely on silence/cap only** — rejected: worse UX for a visitor who wants to explicitly end the conversation (e.g. says "thanks, bye") rather than just walking away.
- **`"thanks"`/`"thank you"` as exit phrases** — deliberately left out: too likely to false-trigger mid-conversation (e.g. "thanks, and what about..."), which would cut a visitor off while they're still asking something. Tracked in `BACKLOG.md` as a known coarse heuristic if real usage shows the current list is wrong in either direction.

## Consequences

- A visitor can now hold a multi-question exchange without pressing the button again, closer to a real conversation.
- The exit-phrase list is a heuristic, not a language model — it will both under- and over-trigger in ways a real NLU system wouldn't. Accepted for this cycle's scope; see `ASSUMPTIONS.md` A-011.
- The 10-turn cap means an unusually long, legitimate Q&A session gets cut off with a goodbye rather than an error — a deliberate trade-off favoring a bounded, predictable demo interaction over an unbounded one.
