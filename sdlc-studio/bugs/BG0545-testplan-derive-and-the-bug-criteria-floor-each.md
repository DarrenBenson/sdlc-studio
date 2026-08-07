# BG0545: testplan derive and the bug criteria floor each mis-slice a checkbox-shaped Acceptance Criteria section, so one refuses a sound plan and the other reports Verify lines that are there as absent

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZCAJX follow-on, 2026-08-07, hit while grooming BG0541. Its four plan rows are sound by the module's own helper and refused by the module's own command.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A bug's criteria are checkbox bullets - `- [ ] **AC1:** ...` with an indented `**Verify:**` line beneath. Two readers slice that shape wrongly, in opposite directions.

`verify_ac.py testplan derive` refuses a plan row for `restating its own criterion - 100% of its substance is the Then clause`. Computed directly with the module's own helpers over the same file, `testplan_row_faults` returns NO faults for that row and `_overlap_ratio` returns 0.0. The refusal path evidently slices the criterion by a heading form the bug body does not use, leaving a degenerate range whose empty substance set scores as total overlap. So a correct plan cannot be re-derived, and the author is told to fix a restatement that is not there.

`transition.py requirements --id <bug> --status Fixed` reports `every acceptance criterion is unticked and none carries a Verify: line` for the same body, while `verify_ac.py run --id <bug>` on that body reports `ac=4` with four verifiers resolved. One of those two statements is false about the same four lines.

This is the family BG0530 was filed for - a writer and a parser that never agreed - one layer along. That bug reconciled `file_finding.py`'s writer with the AC parser; these two readers were not part of the reconciliation.

## Steps to Reproduce

1. Take any bug whose Acceptance Criteria use the shipped checkbox form with an indented `**Verify:**` line, and give it a `## Test Plan` table with a mutant that does not restate its criterion. 2. `verify_ac.py testplan derive --unit <id> --dry-run` refuses with a 100% overlap claim. 3. In a Python shell, call `verify_ac.testplan_row_faults(row, then, affects)` for that row: it returns `[]`, and `_overlap_ratio` returns 0.0. 4. `transition.py requirements --id <id> --status Fixed` says no criterion carries a Verify line; `verify_ac.py run --id <id>` reports four.

## Proposed Fix

Both readers should slice criteria through the one parser that already handles both shapes - the AC bullet and heading forms `verify_ac.run` uses - rather than each carrying its own idea of where a criterion starts and ends.

The overlap check needs a second repair whatever the slicing: an EMPTY substance set must not score as 100% overlap. A ratio over nothing is not a restatement, and reporting it as one is the same false-positive shape that made the edit-verb list refuse honest mutants (BG0534).

Both directions need a test carrying the house bug template verbatim, or the two readers drift apart again the moment either changes - which is exactly what happened here after BG0530 reconciled the writer with a third reader.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A bug's criteria are checkbox bullets - `- [ ] **AC1:** ...` with an indented `**Verify:**` line beneath.
- [ ] **AC2** The proposed fix lands, pinned by a test: Both readers should slice criteria through the one parser that already handles both shapes - the AC bullet and heading forms `verify_ac.run` uses - rather than...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
