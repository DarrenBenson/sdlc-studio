# BG0202: confinement roster sweep misses path.open(mode) so a writer can report no write surface

> **Status:** Open
> **Verification depth:** functional (reproduced directly against _write_surface)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`_write_surface` in `test_confinement.py` reads a file mode from args[1] of a Call, which only matches the BUILTIN form open(p, 'a'). The Path method form path.open('a') passes the mode as args[0] and is not matched at all, so the AST detector reports an empty write surface for a module that demonstrably appends to a file. ConfinementRosterSweepTests then neither cases nor allowlists it: an uncovered writer passes the sweep silently, which is the exact failure the sweep exists to prevent. Proven directly: `_write_surface(`'open(p, "a")') returns {'open:a'} while `_write_surface(`'with path.open("a") as fh: fh.write(1)') returns set(). telemetry.py uses this form at two sites and is covered only incidentally, because it separately calls `atomic_write`; a module whose ONLY write is path.open(mode) would slip the roster entirely. Found while building US0221, whose first implementation used the Path form and was reported as having no write surface.

## Steps to Reproduce

1. cd .claude/skills/sdlc-studio/scripts. 2. python3 -B -c "import sys; sys.path.insert(0,'tests'); sys.path.insert(0,'.'); from `test_confinement` import `_write_surface`; print(`_write_surface(`'with p.open(\"a\") as fh: fh.write(1)'))". 3. Observe set() - no write surface detected. 4. Compare `_write_surface(`'open(p, \"a\")') which returns {'open:a'}.

## Proposed Fix

In `_write_surface`, handle the Path-method call shape as well as the builtin: when the callee is an attribute named 'open', read the mode from args[0] rather than args[1]. Add a unit case for each form beside the existing open:w case, and re-run the roster sweep to see whether any module was being covered only by accident.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
