# BG0589: the close pre-flight counts advisory rows as unmet prerequisites

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Verification depth:** functional (AC2 and AC3 drive BOTH real renderers and pin the full headline line, not a substring - the first cut asserted the library helper alone for AC3 while the criterion says 'either renderer', and a review reworded each print statement in turn and watched the suite stay green; AC2 asserts the two OUTPUTS agree rather than that a helper exists, which a renderer can ignore. Mutation: 4 mutants, each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 4 KILLED, restore byte-exact - including one reverting EACH renderer independently, because fixing one and leaving its sibling lying is the scope error that rejected BG0582 at round two)
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

- [x] **AC1** Given a pre-flight carrying blocking and non-blocking rows, when `_report_preflight` prints its headline, then the noun `unmet prerequisite(s)` carries the BLOCKING count, with the total stated beside it - `8 unmet prerequisite(s) (3 blocking)` keeps the overstatement this bug is about.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_the_headline_noun_carries_the_blocking_count
  - **Verified:** yes (2026-08-18)
- [x] **AC2** Given the same rows, when `_render_preflight` prints, then it reports the same two numbers as `_report_preflight` - both read ONE helper, because fixing one renderer and leaving its sibling lying is the exact scope error that rejected BG0582 at round two.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_both_renderers_agree_and_read_one_helper
  - **Verified:** yes (2026-08-18)
- [x] **AC3** Given a pre-flight whose rows all block, when either renderer prints, then its headline is byte-identical to today - no cosmetic churn for the common case.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_an_all_blocking_page_is_unchanged
  - **Verified:** yes (2026-08-18)

- [x] **AC4** Given a root the command is pointed at, when `sprint.py preflight` is driven as a SUBPROCESS, then its headline is the one `preflight_headline` produces for that same root - the wiring test, and derived from the helper rather than hardcoded so it asserts that the command REACHES the code, never that a tree is in a particular state.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_the_shipped_cli_prints_the_two_numbers
  - **Verified:** yes (2026-08-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | Fixed. `preflight_headline` is the one helper both renderers read |
| 2026-08-18 | sdlc-studio | APPROVED by both seats. AC3 strengthened anyway: it named both renderers and tested only the helper, so churn in either print statement went unseen |

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | render `len(blockers)` in the headline again, so the noun carries the total | Given a pre-flight carrying blocking and non-blocking rows, when `_report_preflight` prints its headline, then the noun `unmet prerequisite(s)` carries the BLOCKING count. |
| AC2 | leave `_report_preflight` computing its own count instead of reading the helper | Given the same rows, when `_render_preflight` prints, then it reports the same two numbers as `_report_preflight`. |
| AC2 | revert `_render_preflight` to its own `len(held)`, fixing only the sibling | Both renderers must read ONE helper - fixing one and leaving the other lying is the scope error this repository keeps meeting. |
| AC3 | always append the `of N reported` suffix, churning the common case | Given a pre-flight whose rows all block, when either renderer prints, then its headline is byte-identical to today. |
| AC4 | render the blocker LIST length in `_render_preflight`, which is the renderer the shipped `preflight` command actually uses - the `_report_preflight` mutant SURVIVED because that renderer serves `close`, not `preflight`, and the ledger refused the mismatch | Given a root the command is pointed at, when `sprint.py preflight` is driven as a subprocess, then its headline is the one `preflight_headline` produces for that same root. |
