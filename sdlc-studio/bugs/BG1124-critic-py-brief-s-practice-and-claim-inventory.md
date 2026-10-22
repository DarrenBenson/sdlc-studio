# BG1124: critic.py brief's practice and claim-inventory refusals read the whole brief, so the unit diff US1094 embeds can satisfy them, and a unit whose own commit removes a practice gets its brief issued

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_checks_ignore_the_diff.py, changelog.d/BG1124.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1094 QA review round 1, qa-seat-US1094-r1, at 7f113429: non-blocking finding 1, with the probe described.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T14:55:47Z

## Summary

US1094's QA review (APPROVE, round 1, 2026-10-22). The standing-practices check and the full-tier claim-inventory check (critic.py around 4019-4021, 4053-4055 and 3410) search the assembled brief, which now includes the UNIT DIFF section. Probe: a brief patched to drop a practice and gut the claim inventory was issued (exit 0) when the unit's committed diff quoted that text, and refused naming the practice when there was no diff. A unit whose own commit removes a practice is briefed because the diff's removed lines carry it. reference-review.md's 'holds by construction' and `cmd_brief`'s 'a deficient brief never reaches a reviewer' over-claim while this stands.

## Steps to Reproduce

Commit a change that removes a standing practice's text from critic.py; brief that unit at the full tier: issued.

## Proposed Fix

Run both checks on the brief with its UNIT DIFF section removed (or on the sections the brief composed, before the diff is appended).

## Acceptance Criteria

- [ ] **AC1** Given a brief whose practices block is missing a practice and whose unit diff quotes that practice's text, when the brief is issued, then it is refused naming the practice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_checks_ignore_the_diff.py::BriefChecksIgnoreTheDiffTests::test_a_practice_quoted_only_in_the_diff_does_not_satisfy_the_check

## Impact

The refusal US1089 and earlier units rely on can be met by quoted text rather than by the brief carrying the practice.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
