# BG0714: 284 added lines of RUN-01M2SPNS are executed by no verifier in the run, and BG0706's proposed fix inherits most of the false charge

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Running all 33 of RUN-01M2SPNS's verifiers in ONE coverage session against the batch's added lines - the run-scope reading BG0706 proposes - leaves 284 added lines that no verifier in the whole run executes. Four of them are substantive, and one is the class of defect this very run shipped a fix for.

## Steps to Reproduce

The panel measured it rather than assuming the run-scope fix would clear the batch:

```text
sprint.py             194 added, 151 executed,  43 uncovered
sprint_report.py      694 added, 627 executed,  67 uncovered
test_sprint.py        539 added, 459 executed,  80 uncovered
test_sprint_report.py 504 added, 454 executed,  50 uncovered
test_run_state.py      46 added,  24 executed,  22 uncovered
test_transition.py     54 added,  43 executed,  11 uncovered
others                                          11 uncovered
TOTAL                                          284
```

About 120 are defensive `except` branches, early-return guards and CLI error printing, and those are honestly ruleable. Four are not:

- `sprint_report.py:3080` - the DORA 'no restore needed' band, a figure an operator reads, on a branch no test sets up.
- `sprint_report.py:3531` - the 'N mutant(s) survived' gap row, which is the report's own honesty machinery.
- `sprint_report.py:3580` - the 'no judges' NOT MEASURED section, exactly the absent-figure honesty this batch was built to guarantee.
- `sprint_report.py:3975` - `file_report` inside `build --write`: the CLI path that files the page of record, reached by no criterion's verifier.

The last is this run's own headline defect in a new place. RUN-01M2SPNS shipped because `stamp_tokens` reached no caller; `build --write`'s filing path is reached by no verifier now.

A further 163 of the 284 sit in the batch's own TEST modules, charged because any `.py` file in `Affects` is measured whatever it is - a test bound to no criterion's `Verify:` selector reads as unreached code. BG0706's proposed run-scope fix inherits that false charge unless it is widened, which is the second half of this finding.

## Proposed Fix

Two parts. (1) Reach the four substantive lines with tests, or rule each with a reason that is true of it. (2) Widen BG0706's run-scope reading so a file in `Affects` that is a TEST module is measured as evidence rather than as production - a test no criterion's selector names is not unreached production code, and charging it that way is 58% of the residue measured here.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Running all 33 of RUN-01M2SPNS's verifiers in ONE coverage session against the batch's added lines - the run-scope reading BG0706 proposes - leaves 284 added...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: The panel measured it rather than assuming the run-scope fix would clear the batch: About 120 are defensive `except` branches, early-return guards and CLI...

## Impact

Two things. First, the four substantive lines are real gaps in the page an operator signs, and one of them is the lane that files it. Second, BG0706's fix as proposed does not clear a batch like this one: measured here, it cuts 5,309 per-unit charges to 284 real lines and then refuses every unit that owns one. Anyone building BG0706 on its current text will finish it and find the gate still red.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
