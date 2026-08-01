# BG0415: The gate budget is OVER at 457s against 380s, and sprint plan forecasts execution cost from the 317s baseline it has already breached by 44%

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (tests red-first: 3 of 7 new criteria failed before the change, the other 4 being fallback and control paths that already held. Two mutants applied singly, purged and restored byte-identical - the measured-series read disabled, and the OVER verdict suppressed: both KILLED. The tracking criterion moves the recorded series and asserts the figure moves, so it cannot be satisfied by the stale baseline read)
> **Affects:** tools/gate_timing.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, tools/tests/test_gate_timing.py
> **Evidence:** `tools/gate_timing.py budget` reports: OVER - 457s of a 380s budget (baseline 317s on 2026-07-26, +44% since). The plan for the next sprint prints `execution policy: per commit SELECTED (~317s); at close FULL (~317s); at release FULL (~317s)` with the basis `gate_budget.baseline_seconds, measured 2026-07-26`. CR0420 already shipped a fix for a stale baseline and is Complete; the baseline has gone stale again since.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

**Review verdict (independent, isolated worktree, fresh context): REJECT on the first delivery.** The planner read `total` while the budget lane reads `total.selected`, so on this repo the two still disagreed - 100s against 554s - and the changelog headline was false as written. Repaired to key on the same `total.last_series` marker, with the series named in the basis. Two dependent defects went with it: an OVER verdict the budget lane did not hold, and a per-commit line over-priced 5.5x. AC4 is unticked: D0089 records the breach as CARRIED, and carrying is not resolving.

## Summary

Two facts that should be one. The budget lane knows the gate now costs 457s against a 380s ceiling. The planner, forecasting the same gate for the same sprint, quotes 317s.

The planner reads `gate_budget.baseline_seconds` - the figure recorded on 2026-07-26 - rather than the recent measured series the budget lane reads. So the plan's own execution-cost line is 44% low, and it is low in the one direction that matters: it under-prices the ceremony whose cost the operator has already challenged once this week.

The error compounds with batch count. The plan says so itself - 'the per-commit figure is paid once per commit that pays it, so this sprint's largest cost is that number times the commits'. A five-batch sprint forecast at 317s per commit budgets about 26 minutes of gate and will pay about 38. That gap is not the interesting part; the interesting part is that the number the operator would use to decide whether the discipline is affordable is the wrong one, and nothing in the plan says which of the two figures to believe.

The second half is that the budget is OVER at all. The ceiling is 380s. The gate is at 457s. CR0420 shipped EP0161 to fix exactly this class - a budget advisory that had become noise rather than a bound - and it is Complete, so the mechanism works and the number has simply drifted past it again with nothing acting on the verdict. An OVER verdict that recurs and is only ever read by a human is a bound in name.

## Steps to Reproduce

1. Run `python3 tools/gate_timing.py budget` - OVER, 457s of 380s, +44% since the baseline.
2. Run `sprint plan` against any worklist - the execution policy line quotes ~317s per commit, three times.
3. `grep -n 'baseline_seconds' .claude/skills/sdlc-studio/scripts/sprint.py` - the forecast reads the pinned baseline, not the measured series the budget lane reads.

## Proposed Fix

1. **One number, one source.** The planner's execution-cost line reads the same recent measured series the budget lane reads, so the plan and the budget cannot disagree about what the gate costs. If a baseline is wanted as well, both are printed and labelled.
2. **An OVER verdict is stated in the plan.** A sprint planned while the gate is over its ceiling says so on the plan, beside the execution policy, because that is the moment the cost can still be traded against scope.
3. **The ceiling is re-derived or the cost is brought back under it** - one of the two, recorded. A ceiling that is breached and left breached teaches everyone to read past it, which is the failure CR0420 was filed for.
4. A test asserts the planner's figure tracks the measured series by moving the series and watching the plan's number move, not by asserting a constant.

## Acceptance Criteria

- [x] The plan's execution-cost figure is derived from the same measured series the budget lane reads, so the two cannot report different costs for the same gate.
- [x] A plan produced while the gate budget is OVER states that verdict on the plan, with the measured seconds and the ceiling.
- [x] A test moves the recorded timing series and asserts the plan's figure moves with it, rather than asserting the current constant.
- [ ] The gate is brought back under its ceiling, or the ceiling is re-derived with the reason recorded - the OVER verdict is resolved rather than carried. **NOT MET, and recorded as not met.** D0089 rules that the ceiling stays at 380s and the breach is carried visibly rather than resolved, because raising it is the pattern CR0510 was filed about and bringing 554s under 380s is a performance project rather than a 3-point unit. Carrying is not resolving; this criterion was ticked in the original delivery while the decision record beside it said the opposite, which an independent review caught. The residue is tracked as BG0415-carry in the retro's known-issues table, ruled `accepted-risk`.

## Impact

The operator asked this week whether the close costs more than the sprint. That question is answered from these two numbers, and they disagree by 44%. Planning is the only point at which gate cost can be traded against scope, so a plan that under-prices it removes the trade.

The wider class is the one this project files bugs about most often: a measurement taken correctly in one place and restated from a stale copy in another. The budget lane is right. The plan is wrong. Both are green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
