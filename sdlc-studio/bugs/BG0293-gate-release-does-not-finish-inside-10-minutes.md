# BG0293: gate --release does not finish inside 10 minutes, so the one lane that judges the whole workspace cannot be run before a release

> **Status:** Fixed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Verification depth:** functional (release lane batching measured end to end: ~874s of pytest spawns to ~453s; mutation-proven by reverting the release-implies-batch wiring and watching the test die; absent-node and skip-is-not-a-pass cases covered)
> **Severity:** High
> **Points:** 5

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Found checking v5 release readiness on 2026-07-24. `gate.py --release` was run with a
600-second timeout and was KILLED before printing a single lane verdict:

```text
timeout 600 python3 .claude/skills/sdlc-studio/scripts/gate.py --release
Exit code 143
```

`--release` is the mode that judges the WHOLE workspace instead of the diff - 431 units and
1,356 artefacts - and it is the only run that may not rely on diff scoping. That property is
exactly why it exists: US0354's diff-scoped speedup made the ordinary gate judge zero units on
a clean tree, and `--release` is the counterweight. So this is the one lane a release cannot
skip, and it currently cannot be completed.

**Cause, measured 2026-07-24 rather than assumed.** The first guess was the whole-workspace
conformance and validate lanes that `--release` swaps in. Both were timed and neither is the
cost: conformance 21.94s, validate 0.63s.

The cost is the `verify` lane, which `--release` adds and refuses to let you deselect. It runs
EVERY acceptance criterion's verifier across the workspace: 1,223 Verify lines, of which 694 are
`pytest` and each spawns its own process. One bare pytest invocation on this repo costs 1.26s
before running a single relevant assertion, so the spawns alone are ~875s - about 15 minutes -
independent of how fast the tests themselves are.

`verify_ac.py` already solves this for the other runner: `--batch` runs jest ONCE and resolves
every jest verifier from the cached result. pytest has no equivalent, so it pays a full process
start per criterion.

Note what this does NOT show: the gate is not proven WRONG, only unrunnable within any usable
timeout. Nothing here says a release would fail its lanes. But an unfinishable check is an
unrun check, and the release cut (US0348) has an acceptance criterion that requires it green.

## Impact

Blocks the v5 cut on its own terms, independently of the backlog. US0348 AC1 cannot be
satisfied. The likely response under time pressure is to skip `--release` and cut on the
diff-scoped gate, which is precisely the failure US0354's review found and repaired.

## Acceptance Criteria

### AC1: the release gate finishes within a stated budget

- **Given** this workspace at its current size (431 units, 1,356 artefacts)
- **When** `gate.py --release` runs
- **Then** it completes and prints a verdict within a budget the gate itself declares and measures, rather than running unbounded - a check with no stated cost is a check nobody runs before a release
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseGateCostTests::test_the_release_gate_completes_within_its_declared_budget

### AC2: the whole-workspace guarantee is not traded away to get there

- **Given** whatever makes it finish - caching, parallelism, or incremental reuse
- **When** a unit is non-conformant anywhere in the workspace
- **Then** `--release` still fails on it. A speedup that reintroduces scoping would recreate the defect `--release` exists to catch, which is the specific trap this repo has already fallen into once
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseGateCostTests::test_a_non_conformant_unit_anywhere_still_fails_the_release_gate

### AC3: the cost is reported, not hidden

- **Given** a completed `--release` run
- **Then** it states how long it took and how much of the workspace it judged, so the next person can tell a fast run from a narrowed one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseGateCostTests::test_the_run_reports_its_duration_and_the_scope_it_judged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
