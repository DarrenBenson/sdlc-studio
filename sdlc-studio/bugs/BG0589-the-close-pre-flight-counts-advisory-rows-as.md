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

- [ ] **AC1** Given a pre-flight carrying blocking and non-blocking rows, when `_report_preflight` prints its headline, then the noun `unmet prerequisite(s)` carries the BLOCKING count, with the total stated beside it - `8 unmet prerequisite(s) (3 blocking)` keeps the overstatement this bug is about.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_the_headline_noun_carries_the_blocking_count
- [ ] **AC2** Given the same rows, when `_render_preflight` prints, then it reports the same two numbers as `_report_preflight` - both read ONE helper, because fixing one renderer and leaving its sibling lying is the exact scope error that rejected BG0582 at round two.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_both_renderers_agree_and_read_one_helper
- [ ] **AC3** Given a pre-flight whose rows all block, when either renderer prints, then its headline is byte-identical to today - no cosmetic churn for the common case.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_an_all_blocking_page_is_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
