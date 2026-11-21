# BG1082: Four of remote-gate doctor's stated behaviours have no test that fails without them

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_doctor_claims.py, changelog.d/BG1082.md
> **Evidence:** US1077 QA review, round 1 (APPROVE), qa-seat-US1077-r1, 2026-10-19, at e849ccc4: finding 3, tools/remote-gate.sh:270, :291, :295, :304.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:25Z

## Summary

Each one, mutated alone, leaves the doctor module green: the no-python3 branch's `exit 1` (as `exit 0` a host with no python3 is ready); the gate-env.sh source (dropped, a host whose Node and packages come from it is NOT ready, against the changelog); archiving HEAD (archiving the working tree lets an uncommitted requirement decide the verdict, against 'sent from this clone's HEAD'); and checking git before gate-env.sh.

## Steps to Reproduce

Apply each mutation to tools/remote-gate.sh in turn and run tools/tests/`test_remote_gate_doctor.py`: it stays green.

## Proposed Fix

Add a test for each: no python3 on the host; Node and a distribution reachable only through gate-env.sh; an uncommitted requirement; git reachable only through gate-env.sh.

## Acceptance Criteria

- [ ] **AC1** Each of the four mutations named in the summary turns the doctor module red
  - **Verify:** pytest tools/tests/test_remote_gate_doctor_claims.py::DoctorClaimTests

## Impact

A later edit can break any of the four with the suite green.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Doctor behaves as documented; four mutation pins are missing for this repository's own gate-host tool. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
