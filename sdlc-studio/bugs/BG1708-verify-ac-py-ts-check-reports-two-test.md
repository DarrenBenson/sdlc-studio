# BG1708: verify_ac.py ts-check reports two test ids pytest collects: a file under a dotted directory in importlib form, and a def whose decorator gives it a docstring with an example

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_ts_check_collected_ids.py, changelog.d/BG1708.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Run twenty-two, BG1534 round three (verdict b7cca454c726-55d4e4ff): both [pre-existing]; the dotted-directory case was AC3 of carry bug BG1703, moved here when BG1703 closed
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T15:38:03Z

## Summary

After BG1534, ts-check resolves a Pass row's test id against what the tree defines, but two shapes pytest collects are still reported as missing. pytest's importlib form for a file under a dotted directory (.hidden/`test_dot.py`::`_hidden.test_dot.f)` is not matched to its module name, and a def whose decorator supplies a docstring holding a doctest example is read by its own (absent) docstring, so its doctest id is reported. Both read the same at 5a7d0b46 and after BG1534's repair (ac5f808c); the qa seat recorded both as pre-existing in BG1534's rounds.

## Steps to Reproduce

1. In a fixture, write .hidden/`test_dot.py` defining f, and a Pass row naming .hidden/`test_dot.py`::`_hidden.test_dot.f`; run `verify_ac.py` ts-check --spec on it: the row is reported. 2. Write a def whose decorator sets `__doc__` to a string with a >>> example, and a Pass row naming that doctest id; ts-check reports it though pytest --doctest-modules collects it.

## Proposed Fix

Map the importlib id's dotted module path for a file under a dotted directory as pytest does, and read a decorated def's doctest from the docstring the decorator returns where it can be read without running the module; pin both with fixture rows that pytest collection also confirms.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: After BG1534, ts-check resolves a Pass row's test id against what the tree defines, but two shapes pytest collects are still reported as missing.
- [ ] **AC2** The proposed fix lands, pinned by a test: Map the importlib id's dotted module path for a file under a dotted directory as pytest does, and read a decorated def's doctest from the docstring the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
