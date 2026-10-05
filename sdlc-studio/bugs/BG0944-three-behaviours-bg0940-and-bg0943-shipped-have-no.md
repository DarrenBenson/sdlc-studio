# BG0944: Three behaviours BG0940 and BG0943 shipped have no test that fails when they break

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T07:47:07Z

## Summary

Found by the QA reviews of RUN-01M45FV6 (qa-s12-bg0940, qa-s12-bg0943), filed under D0338. (1) config.py:55 skips only a null SECTION when merging; widening the guard to skip any null (so a project's deliberate leaf null such as `review.max_rounds:` is ignored) survives `test_lean_config_keys_after_list.py`, `test_config.py` and the `show_sources`/`keys_read`/`code_defaults` suites. (2) BG0940's AC1 clause 'a ruling logged after a reopen is counted' is pinned only for a reopen from a running run: the mutant `_page_filed(state)` -> `state.get("report")` in `run_state.record_ruling` (`run_state.py` ~1756) survives every related module, though a close-sign-reopen-rule probe kills it. (3) The not-judged fallback in sprint.py `_page_no_longer_matches` (~9654-9661) is unpinned: dropping the ReportError catch (sign then crashes) or the predates exemption survives the suite.

## Steps to Reproduce

Apply each mutant above in a scratch copy and run the named suites: all stay green.

## Proposed Fix

Add one test per behaviour, each named for the mutant it kills: a project leaf null overrides the default while a null section does not; a ruling after reopening a SEALED run is counted; sign on a page whose re-derive raises ReportError signs with its note rather than crashing. No production change.

## Acceptance Criteria

- [ ] **AC1** Given a project .config.yaml setting `review.max_rounds:` to null and another whose `review:` section holds only comments, when config.get and config.py show --key `review.max_rounds` run, then the first reads null and the second the shipped default. Fails on: a merge guard that skips every null
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_a_leaf_null_still_overrides
- [ ] **AC2** Given a run closed, signed and then reopened, when decisions.py add --by operator logs a ruling, then the run's rulings count it. Fails on: `record_ruling` withholding a ruling whenever the state holds a report
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_a_ruling_after_reopening_a_sealed_run_counts
- [ ] **AC3** Given a filed page whose re-derive raises ReportError, when sprint sign runs, then it signs on the report alone and prints its note rather than crashing. Fails on: the ReportError catch removed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_an_unjudgeable_page_signs_with_its_note

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | sdlc-studio | Filed |
