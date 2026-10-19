# BG1065: The gate's 45-second cost budget is exceeded on every run (127 s locally, 143 s in CI, the conformance lane alone 121 s), so its OVER line carries no signal

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py, changelog.d/BG1065.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RV0028 finding TSD-12; sdlc-studio/.local/gate-cost.json 127.45 s; CI run 38886029272; gate.py:1825-1833.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:52Z

## Summary

gate.py:1829-1833 sets `GATE_BUDGET_S` = 45 'against a MEASURED 33s for the standard lane set' and warns that 'a warning that always fires is already switched off'. It now always fires: the local cost record reads 127.45 s (2026-10-18), CI run 38886029272 printed 'gate cost: 143.4s - OVER the 45s budget by 98.4s; dominant lane: conformance at 120.8s', and the commit budget of 90 s was exceeded by 7 of the last 10 commits. The TSD names this budget as the performance NFR's proxy.

## Steps to Reproduce

Run `python3 .claude/skills/sdlc-studio/scripts/gate.py` on a clean main -> 'gate cost: ... OVER the 45s budget'; read the CI Lint log's gate step -> conformance dominant at ~121 s.

## Proposed Fix

Find why conformance costs 121 s and cut it, or re-derive the budget from a recorded measurement as gate.py:1830-1832 instructs and cite the source.

## Acceptance Criteria

- [ ] **AC1** On a clean tree at main the standard gate's recorded cost is within its budget, or the budget is re-derived from a cited measurement
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py -k budget_cites_its_measurement

## Impact

The performance NFR's only proxy is permanently red, so a real slowdown is indistinguishable from the standing breach.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
