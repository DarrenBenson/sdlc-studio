# CR-0217: living personas are the explicit default for reviews, critics and consults

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator-requested. The killer differentiator - Alan Cooper's goal-directed personas brought to life as working seats that consult, score, review and hold the independence gate - exists as machinery (`persona_resolve`, amigo cards, consult, WSJF seat inputs) but the workflows do not make it the explicit default: this sprint's own plan ran on 'priority fallback (no seat inputs)' and its critics were hand-named rather than seat-resolved. The skill should say, mechanically and in its reference flows, that a review/critic/consult resolves its seat through `persona_resolve` unless the operator opts out.

## Acceptance Criteria

- [ ] The critic/review reference flows (sprint close, unit critic, repo review) instruct resolving the reviewing seat via `persona_resolve` (review render) and passing that framing to the critic - hand-typed reviewer identities are the fallback, not the norm
- [ ] sprint plan's 'no seat inputs' advisory names the consult command that produces them, so the seat-scoring loop is one step away, not tribal knowledge
- [ ] SKILL.md/persona help state the living-persona principle in one line: personas are working seats, not static artifacts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
