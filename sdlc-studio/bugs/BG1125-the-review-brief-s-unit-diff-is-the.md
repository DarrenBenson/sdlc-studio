# BG1125: The review brief's unit diff is the whole run's diff over the unit's files, not the unit's own change, so on a shared file the 400-line cap is spent on other units' work and the unit's own hunks are cut

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py, .claude/skills/sdlc-studio/scripts/tests/test_unit_diff_is_the_units_own.py, changelog.d/BG1125.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1094 QA review round 1, qa-seat-US1094-r1, at 7f113429: non-blocking finding 2.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T14:56:32Z

## Summary

US1094's QA review (round 1, 2026-10-22). `critic.py brief` diffs the run's base ref to HEAD over the unit's Affects (as AC1 names). In run three all 18 units share one base, so US1094's own full brief spent its 400 lines on US1087's and US1088's self-check work in critic.py (traced with `git log -S` to 71fc1ff7 and 45944907) and cut every US1094 hunk in `_unit_diff_section`, `_verify_section` and `brief()`. A reviewer handed that diff is shown the wrong change. Same root as BG1117/BG1121 (no notion of a unit's own commits) and BG1108 (a carried unit's empty diff).

## Steps to Reproduce

Brief US1094 at the full tier on main after 57d72803: the UNIT DIFF section holds US1087/US1088 hunks and names US1094's files as cut.

## Proposed Fix

Diff the unit's own commits: those whose subject names the unit id since the run's base (each against its parent), restricted to Affects; fall back to the run-base diff, saying so, when no commit names the unit.

## Acceptance Criteria

- [ ] **AC1** Given two units' commits to one Affects file since the run's base, when one is briefed, then its UNIT DIFF holds only the hunks of commits naming that unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_unit_diff_is_the_units_own.py::UnitDiffOwnTests::test_the_diff_holds_only_the_units_own_commits

## Impact

On any shared file the brief's embedded diff, the thing US1094 added to save reviewer turns, shows other units' work instead of the unit's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
