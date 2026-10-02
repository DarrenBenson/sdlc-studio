# BG0906: Two of D0304's time-to-restore rules are unpinned: the FIRST success restores, and an in-progress run ends no streak

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_time_to_restore.py
> **Evidence:** BG0891 QA review round 2 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T13:45:34Z

## Summary

BG0891 ships D0304 correctly, but a mutant letting a later success overwrite a restored incident, and one restoring on any run after a failure, both survive the full suite: on AC1's fixture plus a second green the first reads 1h 50m, and a red run followed only by an in-progress run reads a duration under the second.

## Steps to Reproduce

1. Apply either mutant in `sprint_report._restore_incidents.` 2. The full suite stays green.

## Proposed Fix

Pin both: a second success after the restoring one leaves 1h 9m, and a failure followed only by an in-progress run reads not restored.

## Acceptance Criteria

- [ ] **AC1** Given AC1's runs plus a second success after 17:19, and separately a failure followed only by an in-progress run, when Time to restore is derived, then the first reads 1h 9m and the second reads not restored. Fails on: either mutant, which the current suite does not catch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dora_restore_pins.py::DoraRestorePinsTests::test_the_first_success_restores_and_a_running_run_ends_nothing
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
