# BG0206: test_reconcile cannot be run by module name, only via discover, and the failure is an unrelated ImportError

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

tests/`test_reconcile.py` imports a sibling  module at module level. That resolves under  but not under , which raises ImportError naming loader. It cost a diagnosis cycle during the close: the mutation gate was handed the module form, refused on a red baseline, and its remedy text suggested a stranded mutant from a killed run - a plausible and completely wrong lead. Sibling test modules run fine either way, so the inconsistency is invisible until it bites.

## Steps to Reproduce

1. cd .claude/skills/sdlc-studio/scripts. 2. python3 -m unittest `tests.test_reconcile.` 3. ImportError: Failed to import test module: `test_reconcile`, from . 4. python3 -m unittest discover -s tests -p `test_reconcile.py` passes.

## Proposed Fix

Import loader the way the other test modules reach their siblings (an explicit sys.path
insert of the tests directory before the import, which several already do), so both
invocations work. Alternatively document the discover-only requirement where the mutation
gate tells the operator what to pass as --test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
