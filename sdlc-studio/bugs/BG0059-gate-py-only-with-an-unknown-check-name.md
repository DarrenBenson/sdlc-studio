# BG0059: gate.py --only with an unknown check name yields a vacuous PASS

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

An `--only` (or skip-everything) selection that matches no registered check runs zero checks
and reports the gate as PASS with exit 0. This is the vacuous-pass class the project's own
LL0008 lesson and the `scope` guard exist to prevent.

## Evidence

- `.claude/skills/sdlc-studio/scripts/gate.py:227-228` -
  `selected = [n for n in registry if (not only or n in only) ...]`.
- `gate.py:245` - `ok = all(... for r in results if r["blocking"])` (vacuously true over an
  empty list).
- `gate.py:263` - `return 0 if report["ok"] else 1`.
- Verified empirically: `run_gate(root, only=['no-such-check'])` returns
  `{'ok': True, 'checks': []}` (reproduced this session, 0 checks).

## Impact

A CI step with a typo'd `--only reconcle` (or a stale check name after a rename) goes
permanently green while running nothing - a silent, misleading pass exactly where the gate is
meant to be the last line of defence (LL0008: a deterministic tool must fail loud, never
report success it did not achieve).

## Steps to Reproduce

1. `python3 gate.py --only no-such-check` (or via `run_gate(root, only=['no-such-check'])`).
2. Observe exit 0 and a PASS report with an empty checks list.

## Proposed Fix

Fail loud when `only`/`skip` name a check not in the registry, or when `selected` is empty -
mirroring the existing `scope` guard that already refuses an empty target.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Reproduced empirically; filed from RV0006 code-level leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
