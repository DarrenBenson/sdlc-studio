# BG0367: The AC-less baseline is not one-way, so a newly filed unit can be added to it and exempt itself

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0515 baselines the units that already reach terminal with no acceptance criteria so US0514's refusal does not block the existing corpus. The baseline is read as a plain set with no rule that it may only shrink, so adding an id to it is a supported way to bypass the criteria floor entirely - the exemption the baseline exists to time-box becomes permanent and extensible.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review. Nothing in the check compares the baseline against its previous contents or against the unit's creation date, so an id created after the baseline was taken is honoured identically to one created before it.

## Proposed Fix

Make the baseline one-way: a unit created after the baseline was taken is never exempt regardless of membership, and a guard reports when the baseline grows. Record the baseline date in the file so the rule has something to compare against.

## Acceptance Criteria

### AC1: a baseline may only shrink

- **Given** each grandfathering baseline and its committed state
- **When** it is checked
- **Then** no id has been added - a baseline grandfathers what ALREADY existed, and adding to it turns a time-boxed exemption into a permanent and extensible one
- **Verify:** pytest tools/tests/test_baselines_only_shrink.py::BaselinesOnlyShrinkTests::test_no_baseline_has_grown_against_the_last_commit
- **Verified:** yes (2026-07-29)

### AC2: the comparison reads the committed state

- **Given** `git show` against HEAD
- **When** it is checked
- **Then** it resolves for every baseline, because if it stopped resolving every assertion above would pass vacuously by taking the no-previous-state branch
- **Verify:** pytest tools/tests/test_baselines_only_shrink.py::BaselinesOnlyShrinkTests::test_the_comparison_reads_the_committed_state
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
