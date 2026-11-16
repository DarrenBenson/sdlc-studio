# BG1502: critic.py self-check record refuses a unit until it claims its changelog.d fragment, though the release cut has already merged that fragment into CHANGELOG.md

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1502.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1501/US1173 repair, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T07:18:00Z

## Summary

In run fifteen, the BG1501 and US1173 repair builder found that `critic.py self-check record` refused both units until each carried a claim on its changelog.d fragment, but `release_cut.py changelog-cut` had already folded both fragments into CHANGELOG.md's 6.4.0 section and removed them. The builder had to word a claim saying the fragment now lives in the 6.4.0 section. A unit repaired after the cut cannot satisfy the rule as written.

## Steps to Reproduce

1. Cut a release with `release_cut.py` changelog-cut.
2. Repair a unit whose fragment the cut consumed.
3. Run critic.py self-check record: it refuses for a missing fragment claim.

## Proposed Fix

When a unit's fragment is absent from changelog.d but its id appears in a released CHANGELOG section, accept a claim on that section (or require none), and say so in the refusal.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run fifteen, the BG1501 and US1173 repair builder found that `critic.py self-check record` refused both units until each carried a claim on its changelog.d...
- [ ] **AC2** The proposed fix lands, pinned by a test: When a unit's fragment is absent from changelog.d but its id appears in a released CHANGELOG section, accept a claim on that section (or require none), and say...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
