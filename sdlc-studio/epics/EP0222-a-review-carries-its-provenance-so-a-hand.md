# EP0222: A review carries its provenance, so a hand-rolled pass is not indistinguishable from a briefed one

> **Status:** Draft
> **Derived Point Total:** 18
> **Parent:** CR0503
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0503. Delivers the work CR0503 requested.

## Story Breakdown

- [ ] [US0707: An evidence or verdict row records HOW it was obtained, and marks a row not produced through `brief`](../stories/US0707-an-evidence-or-verdict-row-records-how-it.md)
- [ ] [US0708: `brief` gains a review KIND beside `--seat`, each emitting the standing practices for that kind](../stories/US0708-brief-gains-a-review-kind-beside-seat-each.md)
- [ ] [US0709: The missing-practice refusal extends to every kind, with a test per kind that strips one practice](../stories/US0709-the-missing-practice-refusal-extends-to-every-kind.md)
- [ ] [US0710: A round run with one reviewer, or two on the same lens, is RECORDED as such](../stories/US0710-a-round-run-with-one-reviewer-or-two.md)
- [ ] [US0711: The agent-facing instructions name the seat path as the only supported route to an adversarial review](../stories/US0711-the-agent-facing-instructions-name-the-seat-path.md)

## Acceptance Criteria (Epic Level)

- [ ] An evidence or verdict row records HOW it was obtained, and a row not produced through `critic.py brief` is marked as such rather than being indistinguishable from one that was - the provenance is the enforcement half; without it every rule below is prose.
- [ ] `brief` gains a review KIND along`--seat`, and each kind emits a prompt carrying the standing practices: unit-closing, repair re-review (the existing `--rejoinder`), sprint-level full-diff, design/plan, audit-lens and security. A kind with no template is refused by name, never silently served the unit-closing prompt.
- [ ] The refusal `critic.py` already applies to a brief missing a standing practice is extended to every new kind, proven by a test per kind that strips one practice and asserts the brief is refused - so a new kind cannot ship a weaker contract than the one it joins.
- [ ] A round run with ONE reviewer, or with two on the same lens, is recorded as such - the review record already owes this and no code enforces it.
- [ ] The agent-facing instructions (AGENTS.md and the shipped `agent-instructions.md`) name the seat path as the only supported route to an adversarial review, so an agent reaching for a generic subagent is departing from a stated rule rather than filling a gap in one.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
