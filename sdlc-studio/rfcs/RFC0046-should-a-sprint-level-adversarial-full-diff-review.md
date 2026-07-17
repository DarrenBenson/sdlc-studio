# RFC-0046: Should a sprint-level adversarial full-diff review satisfy the per-unit critiqued gate for a large batch?

> **Status:** In Review
> **Decomposed-into:** EP0080
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close's CODE leg is one rigorous adversarial full-diff pass (independent instance, refute framing, a reproduction per claim). But the conformance 'critiqued' gate and the sign-off brief are per-unit: at the RUN-01KXQH64 close the brief flagged '(no critic verdict recorded)' for all 29 bugs, because the review was recorded at sprint-diff level, not 29 times. Recording 29 per-unit verdicts is heavy and arguably WEAKER than one full-diff pass that caught a real cross-unit regression (BG0181). There is a genuine tension between per-unit accountability and the sprint-level pass the doctrine itself calls the sharper gate.

## Design Options

- **A) Keep per-unit verdicts mandatory - the sprint pass is additional, and every unit still needs its own recorded critic verdict (status quo; heavy for large batches).**
- **B) Let a recorded sprint-level adversarial-review verdict (naming the diff range and the reviewer seat) satisfy the per-unit 'critiqued' stage for the units in that range, with per-unit REJECT-repairs still recorded per unit.**
- **C) Scale by risk: per-unit verdicts for code/logic/security units, sprint-level pass suffices for mechanical/doc units - the review-depth ladder already in reference-sprint.md, extended to the recording requirement.**

## Recommendation

Lean B or C: the full-diff pass is the doctrine's own sharper gate and it caught the cross-unit regression; the recording model should not force 29 shallow per-unit verdicts that are weaker than one deep pass. Explore whether the sign-off brief should read a sprint-level verdict as coverage rather than reporting every unit as unreviewed.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
