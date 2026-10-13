# BG1034: Sign's predates exemption has no pin, and BG0944's reopen pin and module selection are weaker than they look

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py, changelog.d/BG1034.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T10:30:08Z

## Summary

From BG0944's round-1 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) Pre-existing: the sign path accepts a page `revalidate` marks as predating tracked records (`if state.get("valid") or state.get("predates"):` in `_page_no_longer_matches`, sprint.py); dropping `or state.get("predates")` survives `test_lean_s12_pins.py`, `test_lean_sign.py` and `test_lean_tracked_run_record.py`, while an isolated probe signs on the real code and is refused under the mutant. BG0944's own Summary named this mutant as item 3 but its criteria left it out, and no other open Bug or CR records it. (2) `test_lean_s12_pins.py`'s reopen pin relies on the shared fixture's sign sealing the run before the reopen and never asserts it: reduce `run.sign(run.close())` to `run.close()` and the pin stays green while its named mutant then survives. (3) Commit-time selection follows direct edges only, so `test_lean_s12_pins.py` is selected for a change to config.py but not to lib/`run_state.py` or sprint.py, whose behaviour two of its pins guard; those pins fail at push rather than at the commit that breaks them.

## Steps to Reproduce

Apply each mutant in a copy of the skill and run `test_lean_s12_pins.py`, `test_lean_sign.py` and `test_lean_tracked_run_record.py`: (1) survives; reduce the reopen pin's setup as described for (2) and the AC2 mutant survives; run `gate.select_tests` for a change to sprint.py for (3).

## Proposed Fix

Pin the predates exemption through `sprint sign` with a page that predates tracked records; assert in the reopen pin that the run was sealed before the reopen; import sprint and `lib.run_state` directly in `test_lean_s12_pins.py` so selection reaches it.

## Acceptance Criteria

- [ ] **AC1** Given a filed page that `revalidate` reads as predating tracked records, when `sprint sign` runs, then it signs, and the test fails when the predates exemption is dropped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_a_page_that_predates_tracked_records_signs
- [ ] **AC2** Given the reopen pin, when the fixture's sign no longer seals the run, then the pin fails rather than passing on a precondition it never checked
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_a_ruling_after_reopening_a_sealed_run_counts
- [ ] **AC3** Given a change to sprint.py or lib/`run_state.py`, when the commit-time selection runs, then it selects `test_lean_s12_pins.py`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_s12_pins.py::S12PinTests::test_the_pins_are_selected_for_the_code_they_guard

## Impact

A later edit can drop sign's predates exemption, or weaken the fixture, with the suite green; the pins it does have reach the code they guard only at push.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
