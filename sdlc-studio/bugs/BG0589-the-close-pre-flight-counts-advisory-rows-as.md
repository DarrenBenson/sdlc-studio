# BG0589: the close pre-flight counts advisory rows as unmet prerequisites

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_report_preflight` prints `N unmet prerequisite(s)` using the full blocker list, including rows that declared themselves non-blocking. `_render_preflight`, in the same file, already counts `held` instead - so one fact has two answers and the louder one overstates. An operator reading `8 unmet prerequisite(s)` when three actually hold the close is being told the close is nearly twice as far away as it is, and a count that cries wolf is one whose real refusals get waved through.

## Steps to Reproduce

Reported by a round-3 adversarial review, 2026-08-17. `sprint.py` `_report_preflight` renders `len(pre['blockers'])`; `_render_preflight` renders the `held` count. Pre-existing, but this diff makes the overcount systematic rather than occasional: every design-rung close now carries exactly one non-blocking row by construction, and the advisory gate lanes add four more on this repository, so a close reporting 8 has 3 that block.

## Proposed Fix

Count `held` in `_report_preflight`, as `_render_preflight` already does, and say both numbers when they differ - `8 prerequisite(s) reported, 3 of them blocking` - so the advisory rows stay visible without inflating the headline. Read the count from one helper rather than computing it twice, which is the defect being fixed rather than repeated.

## Acceptance Criteria

- [ ] **AC1** Given a pre-flight carrying blocking and non-blocking rows, when `_report_preflight` prints its headline, then the count of BLOCKING rows is stated distinctly from the total
- [ ] **AC2** Given a pre-flight whose rows all block, when it prints, then the headline is unchanged from today - no cosmetic churn for the common case

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
