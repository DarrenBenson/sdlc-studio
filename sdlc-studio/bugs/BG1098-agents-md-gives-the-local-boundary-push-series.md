# BG1098: AGENTS.md gives the local boundary-push series as the push's cost on a clone that names a gate host

> **Status:** Won't Fix
> **Supersedes:** BG1105
> **Severity:** Low
> **Points:** 1
> **Affects:** AGENTS.md, tools/tests/test_agents_push_cost_series.py, changelog.d/BG1098.md
> **Evidence:** US1086 QA review, rounds 1 and 2, qa-seat-US1086-r1, 2026-10-19: [pre-existing] item.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T20:49:08Z

## Summary

AGENTS.md says `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0` prints the current push figure. On a clone with sdlc.gateHost set, the pre-push hook records the host's run under its own series (boundary-push@<host>, .githooks/pre-push:222 and :259), which never enters the local one, so the command prints a figure no push here produces (about 2957 s against about 592 s on devserver1, 2026-10-19).

## Steps to Reproduce

On this clone (sdlc.gateHost devserver1), compare `gate_timing.py estimate --suite boundary-push` with `--suite boundary-push@devserver1`.

## Proposed Fix

Name both series in AGENTS.md, as the TSD now does.

## Acceptance Criteria

- [ ] **AC1** AGENTS.md names the gate host's series beside the local one
  - **Verify:** pytest tools/tests/test_agents_push_cost_series.py::AgentsPushCostSeriesTests

## Impact

An agent budgets a push at the wrong cost.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. AGENTS.md of this repository names only the local series; it concerns clones with a gate host, and the TSD names both. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
