# BG0707: the corpus baseline's CI-run line is judged by shape alone, so a hand-typed run id reads as a re-measure

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/tests/test_lint_workflow_coverage.py, tools/verify-corpus-baseline.txt
> **Evidence:** BG0676 engineering delivery verdict, RUN-01M2JA6J 2026-09-16, brief 6e7699f22695.
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0676 AC4 opens 'the red-criteria baseline is re-measured from a CI corpus-verify run taken with AC3's override in force, never a local one', but its test (tools/tests/`test_lint_workflow_coverage.py`:33, `_RUN_LINE`) checks only that a line matching `# re-measured from CI run <digits>` exists. Replacing the real id 35072360410 with `1` leaves the test green, and nothing in the fixture separates a CI re-measure from an invented one: the criterion's words reach the provenance of the number, the fixture reaches its punctuation. Raised by the engineering seat at BG0676's delivery review, which settled the substance by hand against the live run (`workflow_dispatch` on d8659180, `SDLC_VERIFY_TIMEOUT`=300 in the step env, 'red-criteria: 19' in the log) - so the shipped baseline is sound and this is about what the guard can prove next time. A check that asks the forge for the run (event `workflow_dispatch`, conclusion of the corpus-verify job, the sha on HEAD's history, the override in its step env) is the shape AC5's own Verify already uses, and it needs `gh` available where the test runs, which is the open question this unit has to settle rather than assume.

## Steps to Reproduce

1. In tools/verify-corpus-baseline.txt, change the `# re-measured from CI run 35072360410` line to `# re-measured from CI run 1`. 2. Run pytest tools/tests/`test_lint_workflow_coverage.py`::CorpusJobEnvironmentTests::`test_the_baseline_names_its_ci_run.` 3. It passes, though no CI run 1 exists for this repository.

## Proposed Fix

Judge the named run, not the line's shape: read it through the forge (as AC5's Verify does), requiring event `workflow_dispatch`, a corpus-verify job, and the override in that job's step environment. Where `gh` is unavailable the check must SKIP by name rather than pass silently - a guard that cannot run must not read as a guard that ran.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0676 AC4 opens 'the red-criteria baseline is re-measured from a CI corpus-verify run taken with AC3's override in force, never a local one', but its test...
- [ ] **AC2** The proposed fix lands, pinned by a test: Judge the named run, not the line's shape: read it through the forge (as AC5's Verify does), requiring event `workflow_dispatch`, a corpus-verify job, and the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - corpus baseline CI-run line checked by shape: test nit on a corpus lane |
