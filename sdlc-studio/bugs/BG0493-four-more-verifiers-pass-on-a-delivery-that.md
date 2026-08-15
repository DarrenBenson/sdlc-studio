# BG0493: four more verifiers pass on a delivery that has been made inert

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/conftest.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/best_practice_rules.py
> **Severity:** Medium
> **Points:** 3

## Summary

The residue of the source-grep verifier class after 307ce91d repaired the blocking half. Each was demonstrated by an independent pass, by mutation.

BG0476 - replacing `sys.path.insert(0, ...)` with `pass` in tools/tests/conftest.py SURVIVES both ACs. AC1's `assertIn("sys.path.insert", conftest.read_text())` is satisfied by the file's own DOCSTRING at line 8. The Resolution's 'deleting conftest.py KILLS the guard' is true of AC1 only; AC2 stays green.

US0606 - AC1's `text.split("lane-check")[1][:600]` lands entirely inside a COMMENT block, so its `assertIn("|| true", block)` is satisfied by an unrelated pipeline. Dropping the lane's own `|| true` survives.

US0607 - `best_practice_rules.py` returns 0 when the practice file is ABSENT, so the exemption is reachable by deleting the file - the shape US0608 AC4 exists to prevent. It is also wired into no gate: no caller in .githooks/, package.json or tools/.

BG0423 - `Verification depth: functional`, but both verifiers are source-text greps over .githooks/commit-msg and nothing executes the hook.

## Triage 2026-08-15

Re-measured before any code was written. **All three instances stand**, so this bug is carried
unnarrowed - the opposite finding to BG0490 beside it, and the reason each was measured rather
than assumed from its age.

| Instance | Measured now |
| --- | --- |
| BG0476 | **STANDS** - `sys.path.insert` appears twice in `tools/tests/conftest.py`, at line 8 in the DOCSTRING and line 15 as the real call, so AC1's `assertIn` is satisfied with the call deleted |
| US0606 | **STANDS** - the `lane-check` slice still opens inside a comment block, and the `\|\| true` its assertion finds belongs to an unrelated pipeline |
| US0607 | **STANDS** - `best_practice_rules.py` is referenced by nothing in `.githooks/` or `package.json`, so it is wired into no gate |

Not built here: each repair is a test-strengthening change to a guard, which is engineering
rather than triage. What triage establishes is that the premise is still real - the three
verifiers named here would still pass over a delivery that had been made inert.

## Steps to Reproduce

For each, apply the named mutant with `__pycache__` purged and python3 -B, and observe the declared verifiers stay green.

## Proposed Fix

Point each verifier at the behaviour: run the hook, run the command, or parse the call graph. `tools/best_practice_rules.py` should fail loudly on an absent practice file and be wired into a lane that runs.

## Impact

Four more criteria that cannot fail. Individually small; together they are why five review passes returned 27 rejections against a batch whose every declared verifier was green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
