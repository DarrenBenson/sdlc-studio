# BG0545: testplan derive and the bug criteria floor each mis-slice a checkbox-shaped Acceptance Criteria section, so one refuses a sound plan and the other reports Verify lines that are there as absent

> **Status:** Fixed
> **Verification depth:** functional (executed: the defect measured on four real units at exactly 100% before the fix and absent after, and the filed mechanism falsified in the process - it is an over-wide range, not a degenerate one; the second half of the bug was re-measured and no longer reproduces; mutation: 2 declared mutants, both KILLED, restore byte-exact)
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

- [x] **AC1** Given a unit whose criteria section is followed by a `## Test Plan`, when its plan is re-derived, then the last criterion's `Then` clause stops at the next heading and the final row is not refused as restating itself.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k last_criterion_does_not_read
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given a mutant whose substance is entirely path tokens, when it is judged, then it is refused for carrying no edit verb and NOT for restating a clause it shares nothing with - a ratio over nothing is not a restatement.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k no_substance_is_not_called_a_restatement
  - **Verified:** yes (2026-08-14)

## Resolution

The filed mechanism was wrong, and measuring it before fixing it is what found the real one. The report guessed at "a degenerate range whose EMPTY substance set scores as total overlap". It is the opposite: an over-wide range. The last criterion's `Then` bound was `len(lines)`, so it ran to the bottom of the artefact and swallowed the Resolution prose, the Revision History and - fatally - the `## Test Plan` table itself, which holds every mutant's own text. The final row's mutant was measured for overlap against a passage containing that mutant and scored exactly 1.0.

That made it deterministic and invisible together: it struck only the last row, and only once a plan already existed, so the first derive of a unit passed and every re-derive failed. Measured on four real units before the fix - BG0553 AC7, BG0556 AC3, BG0576 AC5, BG0555 AC3 - all at 100%. No fixture in the derive suite had a plan when it derived, which is why 303 passing tests never saw it.

`_then_clause`'s own docstring records the same shape being paid for once already, where a mis-stripped bullet fell through to a block carrying the mutant. Both are one fault: a range wide enough to include the answer.

The empty-set half of the proposed fix was real but smaller than filed: `_overlap_ratio` returned 1.0 over an empty set, so a mutant made only of path tokens was refused for restating a clause it shares no word with. The refusal was correct and its stated reason false, which sends an author to fix something that is not there.

**The second half of this bug no longer reproduces.** `transition.py requirements` and `verify_ac.py run` now agree about a checkbox-shaped body; the AC parser widening earlier in this run reconciled them. Verified before any code was written here rather than assumed.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in verify_ac.py, bound the last criterion at len(lines) again so its Then clause swallows the plan table | Given a unit whose criteria section is followed by a `## Test Plan`, when its plan is re-derived, then the last criterion's `Then` clause stops at the next heading and the final row is not refused as restating itself. |
| AC2 | in verify_ac.py `_overlap_ratio`, return 1.0 for an empty substance set again | Given a mutant whose substance is entirely path tokens, when it is judged, then it is refused for carrying no edit verb and NOT for restating a clause it shares nothing with - a ratio over nothing is not a restatement. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
