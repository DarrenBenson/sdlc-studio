# CR-0368: conformance reports a unit missing critiqued without naming which half is unmet

> **Status:** In Progress
> **Decomposed-into:** EP0132
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The critiqued stage is one boolean composed of up to three independent halves: an APPROVE verdict with proven author-reviewer independence, an adversarial pass recorded as evidence, and an independent reviewer-of-record sign-off (the last two only past `review.two_role_after).` Conformance reports only 'missing critiqued', so the operator cannot tell which half is owed. Hit live this session: a verdict was recorded, conformance still said missing critiqued, and the answer was only findable by reading the composition logic in the source. The remedy line points at running `verify_ac` and back-annotating, which is the remedy for a DIFFERENT stage and does not clear this one.

## Impact

Anyone closing a unit past the two-role cutoff has to read conformance's source to learn what the gate wants. A gate whose diagnostic does not name the unmet condition costs a source dive per occurrence, and the printed remedy actively misdirects toward the verified stage.

## Acceptance Criteria

- [ ] Given a unit missing only the reviewer-of-record sign-off, when conformance reports it, then the output names the sign-off specifically rather than the composite stage
- [ ] Given a unit missing several halves at once, when conformance reports it, then every unmet half is named in one line, not just the first
- [ ] Given a unit whose critiqued stage is satisfied, when conformance runs, then it is reported conformant exactly as today - the change is diagnostic detail, not a new refusal

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
