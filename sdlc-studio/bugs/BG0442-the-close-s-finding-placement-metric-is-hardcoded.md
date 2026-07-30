# BG0442: the close's finding-placement metric is hardcoded to zero by its own repair's import, so the number the sprint goal is driven to is a constant the code cannot compute

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** The comment directly above the call states the defect this code was written to repair: "The line read identically for 0 close-time findings and for 10,000." That is still true, and the cause is now the repair's own import. This is the recurring class CR0504 names - prose promising what no code path implements - in the sharpest form yet found, since the prose is a repair claim about the exact symptom that is still live three lines below it.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** engineering amigo seat (independent, isolated worktree), reproduced by author; human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint._findings_outside_batches` opens with a function-local `import run_state`. The module is `lib/run_state.py` and sprint.py already binds it at module scope as `from lib import run_state`; the local statement shadows that binding and always raises ImportError, because `lib/run_state.py` begins `from . import sdlc_md`, a relative import no top-level import can satisfy. A blanket `except Exception` returns 0, and the diagnostic goes to `sdlc_md.debug`, which is a no-op unless `SDLC_DEBUG`=1. So the function is unreachable code returning a constant, silently, on every default run. The line it feeds reads "N raised outside one ... `outside` is the number this run drives to zero" - a metric that is always already zero, printed as though measured.

## Steps to Reproduce

Executed on this repository at d7a1ad8f, 2026-07-30.

```text
`SDLC_DEBUG`=1 python3 -c "
import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts')
import sprint
print('module-level:', `sprint.run_state.__name__)`
try:
    import `run_state`; print('bare import OK')
except Exception as e: print('bare import FAILS:', e)
print('result:', `sprint._findings_outside_batches(`'.', []))
"
```

Actual output:

```text
[sdlc-debug] `sprint._findings_outside_batches`: No module named '`run_state`'
module-level: `lib.run_state`
bare import FAILS: No module named '`run_state`'
result: 0
```

The reviewer who found it built a temp repo with TEN findings, every one stamped `Raised-in-batch: none open - raised outside a delivery batch`, and the close still printed `finding placement: 0 raised at a batch boundary, 0 raised outside one`.

A fix-mutant restoring the correct import made it report the true count. `test_sprint.py` ran 606 tests OK both with and WITHOUT that mutant: no test names this function, so the behaviour is unpinned in both directions.

Found by the engineering amigo seat during the close of RUN-01KYPZ1G, then reproduced independently by the author before filing.

## Proposed Fix

1. Delete the function-local import and use the module-level `run_state` binding that is already correct. The local statement adds nothing even when it works.
2. Pin it with a test that constructs findings raised outside a batch and asserts the reported count is that number, not merely that the line renders. The absence of such a test is why a constant passed for a measurement, and why the fix-mutant changed no test outcome.
3. The blanket `except Exception -> return 0` is the reason this was invisible for a whole sprint. A reporting clause should not fail a close, but returning a number indistinguishable from a real measurement is worse than failing: the honest fallback is to report the figure as UNKNOWN, on the same principle this repo already applies to a dead-flag destination it cannot judge. A silent zero asserts the good outcome.

Worth noting during refine: even with the import repaired, the loop applies no run or date filter - `started_at` is used only as a truthiness gate - so the count would span every bug and CR in the workspace rather than the ones this run raised. That is a second defect behind the first, and fixing the import alone would turn a false zero into a false large number.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sprint._findings_outside_batches` opens with a function-local `import run_state`.
- [ ] Following the recorded steps no longer reproduces the defect: Executed on this repository at d7a1ad8f, 2026-07-30.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree), reproduced by author | Filed |
