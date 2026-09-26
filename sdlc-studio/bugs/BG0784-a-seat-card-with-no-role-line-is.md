# BG0784: A seat card with no role line is silently bypassed for the shipped card, and the unknown-seat refusal names the wrong seats

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T12:08:53Z

## Summary

After US0950, critic.py brief resolves seats through `persona_resolve.resolve_card`: a sdlc-studio/personas/seats/<seat>.md without a role line is ignored and the shipped card briefs the reviewer, with no warning. The unknown-seat refusal names the fixed list (engineering, qa, product), not the project's cards, and `test_unknown_seat_refused_naming_available` passes on that fixed list. Found by US0950's QA review.

## Steps to Reproduce

Write seats/qa.md with no role line; run critic.py brief --seat qa: the shipped charter is briefed silently.

## Proposed Fix

Warn on stderr when seats/<seat>.md exists without a role line; name the project's declared roles and role-less cards in the refusal, and make the test assert them.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: After US0950, critic.py brief resolves seats through `persona_resolve.resolve_card`: a sdlc-studio/personas/seats/<seat>.md without a role line is ignored and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write seats/qa.md with no role line; run critic.py brief --seat qa: the shipped charter is briefed silently.
- [ ] **AC3** The proposed fix lands, pinned by a test: Warn on stderr when seats/<seat>.md exists without a role line; name the project's declared roles and role-less cards in the refusal, and make the test assert...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
