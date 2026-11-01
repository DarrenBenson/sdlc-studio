# BG1065: The gate's 45-second cost budget is exceeded on every run (127 s locally, 143 s in CI, the conformance lane alone 121 s), so its OVER line carries no signal

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Depends on:** BG0963
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

- [ ] **AC1** `GATE_BUDGET_S` is re-derived from a measured standard-gate run recorded beside it as data (seconds, date, commit), and is not below that measurement
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py::GateBudgetTests::test_the_budget_is_not_below_its_recorded_measurement

## Impact

The performance NFR's only proxy is permanently red, so a real slowdown is indistinguishable from the standing breach.

## Further evidence

- 2026-10-20, cProfile of `gate.py --root .` on a clean tree at fd16f28a (workstation, quiet): gate cost 330.0 s, conformance 280.2 s over the whole workspace (1086 units). Within conformance, `critic.read_verdicts` is called once per unit (812 times) and re-parses the verdict ledger each time, for 125 s, of which `sdlc_md.table_cells` is 51 s. `verify_ac._collect_nodes` spawns 257 collection subprocesses, for 130 s. In engagement-floor (31.7 s), `decisions.list_decisions` is called 2229 times through `waiver_for`, for 27.6 s. Those three account for about 283 s of the 330 s.

## Notes

- From BG0963 (2026-11-01): gate.py's serial_only description still says only global tree state; also name wall-clock upper bounds, which BG0963 marks serial_only and boundary_only. A docstring change to gate.py selects a very wide module set at commit (1072 s measured), so make it in this unit's own gate.py commit.
- Pre-run baseline, 2026-10-31 at 62fc405a: a standard `gate.py` run took 38.6s against the 45s budget (engagement-floor 26.3s), so the run is no longer over budget on every run. The AC still holds: the budget is recorded beside a measurement, so the OVER line means something again.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-20 | Claude Opus 5.5 | Further evidence: a profile of the conformance and engagement-floor lanes on a clean tree |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-10-31 | Claude Opus 5.5 | Run-four plan (D0392): depends on BG0963, which shares a file this unit declares |
| 2026-10-31 | Claude Opus 5.5 | Pre-run gate baseline recorded for the run-four goal review (D0393) |
