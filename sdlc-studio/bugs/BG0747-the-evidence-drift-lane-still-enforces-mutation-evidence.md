# BG0747: The evidence-drift lane still enforces mutation evidence that D0255 switched off, and re-registration drops other rows

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0255 set `review.mutation_evidence`: off, but gate.py's evidence-drift lane still blocks any commit that drifts a registered mutant row. RUN-01M36R3D paid for it by re-applying and re-registering 31 unanchored rows (BG0497, BG0623, BG0624, BG0591, BG0616, BG0646, BG0719). Re-registering BG0719's one drifted row dropped its 12 other anchored rows on `sprint_report.py`, because register discards every row whose recorded bytes changed (the LL0053 class). The lane should follow the mode, and the ledger is on the deletion list.

## Steps to Reproduce

Stage an edit to a file that holds unanchored registered mutant rows of a delivered unit, with `review.mutation_evidence`: off: the commit is refused by evidence-drift.

## Proposed Fix

Make evidence-drift honour `review.mutation_evidence` (off -> report only), and stop `register` from dropping anchored rows whose site did not move; long term, delete the ledger with the lane.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: D0255 set `review.mutation_evidence`: off, but gate.py's evidence-drift lane still blocks any commit that drifts a registered mutant row.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Stage an edit to a file that holds unanchored registered mutant rows of a delivered unit, with `review.mutation_evidence`: off: the commit is refused by...
- [ ] **AC3** The proposed fix lands, pinned by a test: Make evidence-drift honour `review.mutation_evidence` (off -> report only), and stop `register` from dropping anchored rows whose site did not move; long term...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
