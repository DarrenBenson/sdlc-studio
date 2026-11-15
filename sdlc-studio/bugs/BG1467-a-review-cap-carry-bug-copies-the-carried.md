# BG1467: A review-cap carry bug copies the carried unit's Affects verbatim, so it declares the unit's changelog fragment, not its own

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1467.md
> **Evidence:** Run thirteen, BG1460's land, 2026-11-15 (sdlc-studio/.local/lane/landed/agent-a4808b05ebc12143e).
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:31:09Z

## Summary

When a unit is rejected at the review cap, critic.py (`carry_at_cap`, near line 2043) files the carrying bug with the carried unit's Affects copied verbatim. Those Affects name the unit's own fragment (changelog.d/US1058.md for BG1460), not the bug's. The builder writes changelog.d/BG1460.md, as the doctrine asks, and `lane land` then commits the lane but refuses the self-check: 'claim 4 names the surface changelog.d/BG1460.md, which the self-check does not name'. No QA brief is written, and the orchestrator has to re-point the Affects with transition.py annotate and record the self-check by hand.

## Steps to Reproduce

1. Reject a unit at the review cap so that critic.py files its carry bug.
2. Build the bug with a changelog.d/<bug id>.md fragment and land it with `sprint.py lane land`.
3. See the self-check refused over the fragment's surface.

## Proposed Fix

When copying the carried unit's Affects, replace its changelog.d/<unit>.md entry with changelog.d/<bug id>.md.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When a unit is rejected at the review cap, critic.py (`carry_at_cap`, near line 2043) files the carrying bug with the carried unit's Affects copied verbatim.
- [ ] **AC2** The proposed fix lands, pinned by a test: When copying the carried unit's Affects, replace its changelog.d/<unit>.md entry with changelog.d/<bug id>.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
