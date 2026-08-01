# BG0413: A suite that loses 90% of its tests is judged not to have covered its scope and is committed anyway - the scope floor declines to record a timing instead of refusing

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Verification depth:** functional (tests red-first: 12 new criteria failed before the change. Six mutants applied singly, anchor asserted unique, `__pycache__` purged, `python3 -B`, each file restored byte-identical - collapse branch disabled, exit 2 downgraded to 1, stale ack accepted, reasonless ack accepted: all KILLED. The reasonless-ack mutant SURVIVED a first attempt because the caller's truthiness test made the explicit guard unreachable; the caller now tests `is not None`, so the rule has one owner)
> **Affects:** tools/gate_timing.py, .githooks/commit-msg, tools/tests/test_gate_timing.py
> **Evidence:** RUN-01KYNKDP close: reverting US0553 replaced a span from `CloseVerdictReuseTests` to `CloseRetryTests` and deleted eight intervening test classes. The suite reported 510 passing against a normal 5,176 and was OK, because deleted tests do not fail. Caught by reading the count, not by any guard. `SCOPE_FLOOR = 0.8` in tools/gate_timing.py would have judged that run as not having covered its scope.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** RUN-01KYNKDP close review; human; v1

**Review verdict (independent, isolated worktree, fresh context): REJECT on the first delivery.** Five findings, each with an executed reproduction: exit 2 colliding with python's own exit 2 (which left a RED test on main), the ack clearing the 0.8 timing floor, a collapsed count evicting the peak over ten instructed retries, a silent acknowledged escape, and a vacuous loader-error test whose `not loader_error` term survived being mutated away. All repaired; four repair mutants applied singly, purged, restored byte-identical, all KILLED. The full `tools/tests` suite is green under the gate's own runner - the original delivery was verified against a SELECTED subset, which is the rule BG0422 shipped one commit later and this one broke.

## Summary

The guard for this exists, would have fired, and its entire consequence is that a number does not get written to a JSON file.

`scope_ok` judges whether a run actually ran its scope or merely got invoked, and `SCOPE_FLOOR = 0.8` means a run losing more than a fifth of the historic peak test count fails that judgement. A run of 510 tests against a peak of 5,645 is a 91% loss - not a marginal call.

What happens on that verdict: `cmd_scope` prints `gate-budget: total NOT recorded - ...` and returns exit 1, the count is appended to the series anyway so the peak keeps improving, and the docstring states the rule outright - "Never raises into a commit." The commit proceeds.

That is correct for what the function was built for. It exists so a truncated run cannot poison the TIMING series (BG0239: a lane that was invoked but whose module failed to import recorded a short run and the budget read '-26% since', a broken suite reading as an improvement). Judged as a budget-hygiene mechanism it is right.

But it is now the only thing in the repository that can notice a suite has stopped running most of itself, and it treats that exactly as it treats a noisy timing: by declining to record. Two very different facts share one consequence, and the louder one is invisible.

The case is not hypothetical. This close deleted eight test classes - the guards for BG0385, BG0354, BG0394, BG0392, BG0395, BG0391, US0555 and US0559 - and the suite went green at 510 tests. It was found by a human reading the count. Had it not been, the commit would have passed every lane and the only trace anywhere would have been a missing entry in `gate-timings.json`.

## Steps to Reproduce

1. Delete a large contiguous span of test classes from a suite module.
2. Run the suite: it reports OK, because a deleted test cannot fail.
3. Commit. `scope_ok` judges the run as not having covered its scope, prints `gate-budget: total NOT recorded`, and the commit lands.
4. Read `sdlc-studio/.local/gate-timings.json`: `total.tests` shows an unbroken series, because the count is appended either way.

## Proposed Fix

Separate the two facts and give the loud one a loud consequence.

1. **A large drop REFUSES the commit.** Below some second, much lower threshold - a collapse rather than a drift - the commit is blocked with the two counts and the peak named. The existing 0.8 floor stays exactly as it is for its own purpose: it is deliberately generous because tests are legitimately deleted, and a floor that fires on real deletions trains people to ignore it. A 90% collapse is not that case.
2. **Deliberate removal has a stated escape**, in the shape this repo already uses for a recorded exception, so a genuine bulk deletion states itself rather than being waved through by a generous threshold.
3. **Say the numbers.** The current message names neither the count nor the peak, so even a reader who sees it cannot tell a rounding wobble from a collapse.
4. Consider not appending the count on a refused scope, or appending it marked - a collapsed run currently feeds the same series used to judge the next one.

## Acceptance Criteria

- [x] A run whose test count collapses against the historic peak REFUSES the commit rather than only declining to record a timing.
- [x] The refusal names the run's count, the historic peak, and the drop, so a reader can tell a collapse from a drift.
- [x] The existing 0.8 floor keeps its current generous behaviour for its own purpose, so a legitimate test deletion is not turned into a blocking event.
- [x] A deliberate bulk removal has a recorded escape, stated on the record rather than passed silently.
- [x] A test asserts the refusal by simulating a collapsed count, not by asserting the constant.

## Impact

This is the guard against the class of mistake that is hardest for a suite to catch by construction: a test that no longer exists cannot go red. Every other lane in this gate is defended by the tests; the tests themselves are defended only by this.

A project whose whole argument is that its records mean something shipped a close in which the suite silently stopped running 90% of itself, and the mechanism built to notice responded by not writing a timing. Anyone reading `gate green.` was reading a true statement about the lanes that ran and a meaningless one about coverage.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | RUN-01KYNKDP close review | Filed |
