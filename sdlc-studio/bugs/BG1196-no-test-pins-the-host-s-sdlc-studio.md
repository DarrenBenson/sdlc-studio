# BG1196: No test pins the host's SDLC_STUDIO_BOUNDARY_SUITE=1 export for remote-gate.sh's push and suite jobs

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_remote_gate_push.py, tools/tests/test_run_suite_remote.py, changelog.d/BG1196.md
> **Evidence:** US1114 round-1 verdict, scratchpad run5/US1114-verdict-r1.txt, mutants in run5/us1114-mut/.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T09:06:04Z

## Summary

2026-11-04, US1114's review (qa-seat-US1114-r1, APPROVE, pre-existing). The push and suite jobs on the gate host export `SDLC_STUDIO_BOUNDARY_SUITE=1` (tools/remote-gate.sh:351, moved there by US1114 from a `SDLC_STUDIO_BOUNDARY_SUITE=1 setsid` command prefix). Deleting the line leaves `test_remote_gate_push.py`, `test_remote_gate_runs.py` and `test_run_suite_remote.py` green (22 passed, 12 subtests), and deleting the prefix at 00525efa left the same three green. US1114's changelog says the push and suite jobs still export it, and no test holds that sentence.

## Steps to Reproduce

1. Delete the `export SDLC_STUDIO_BOUNDARY_SUITE=1` line in the non-release branch of tools/remote-gate.sh.
2. `python3 -m pytest -q tools/tests/test_remote_gate_push.py tools/tests/test_remote_gate_runs.py tools/tests/test_run_suite_remote.py`: all pass.

## Proposed Fix

Have the stub host record the environment its gate receives on a push and a suite job, and assert `SDLC_STUDIO_BOUNDARY_SUITE`=1 in each.

## Acceptance Criteria

- [ ] **AC1** Deleting the host's export of `SDLC_STUDIO_BOUNDARY_SUITE`=1 for the push or the suite job fails a test.
  - **Verify:** pytest tools/tests/test_remote_gate_push.py tools/tests/test_run_suite_remote.py

## Impact

A later edit can drop the switch from the host's push gate, so boundary-only tests stop running there, with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
