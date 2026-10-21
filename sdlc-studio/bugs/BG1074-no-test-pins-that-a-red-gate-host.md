# BG1074: No test pins that a red gate-host run records its duration, so the hook can stop recording exit 1 with the suite green

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_remote_gate_push.py, changelog.d/BG1074.md
> **Evidence:** US1075 round-2 QA verdict (sdlc-studio/reviews/critic-verdicts.md), its [new] finding; .githooks/pre-push host-path record condition.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T13:07:45Z

## Summary

The pre-push hook records a host run's duration only when remote-gate.sh exits 0 or 1, the two codes that mean the host's gate ran. `test_remote_gate_push.py` pins exit 0 (AC5) and pins that exits 2 and 4 record nothing, but no test pins exit 1: narrowing the hook's condition from `-ne 0 ] && [ "$rc" -ne 1` to `-ne 0` stops a red host run from recording, and every test passes. remote-gate.sh's header and US1075's changelog both claim 'only 0 and 1'. Found by US1075's round-2 QA reviewer as a non-blocking [new] finding.

## Steps to Reproduce

Edit .githooks/pre-push's host-path record condition to `[ "$rc" -ne 0 ]`, then `pytest tools/tests/test_remote_gate_push.py` -> all pass.

## Proposed Fix

Assert in the red-host-run case (AC1's) that the host series gains a run.

## Acceptance Criteria

- [ ] **AC1** A red host run's duration is recorded under the host's suite, and a test fails when it is not
  - **Verify:** pytest tools/tests/test_remote_gate_push.py::RemoteGatePushTests::test_a_red_host_run_records_its_duration

## Impact

A red host run could silently stop entering the cost estimate the next push announces.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
