# BG0757: repo_map.py build crashes on Python 3.10 when a source file holds a null byte

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py
> **Evidence:** US0908 review round 1, RUN-01M39MC0: the whole skill suite run under a 3.10 venv
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repo_map.py` catches only SyntaxError around `ast.parse` (`repo_map.py`:178-180). Python 3.10 raises ValueError for a source string containing a null byte, so `repo_map.py build` exits 1 with 'source code string cannot contain null bytes' on 3.10, where 3.11+ raise SyntaxError and the build continues. `test_repo_map.py`::BuildRobustnessTests::`test_binary_garbage_in_source_does_not_crash` fails under 3.10. The skill declares 3.10 as its floor, so consumers on 3.10 hit it.

## Steps to Reproduce

1. Put a .py file containing a null byte in a fixture repository. 2. Run `python3.10 .claude/skills/sdlc-studio/scripts/repo_map.py build` against it. 3. It exits 1; under 3.12 it exits 0.

## Proposed Fix

Catch ValueError beside SyntaxError where the source is parsed, and treat it as an unparseable file.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `repo_map.py` catches only SyntaxError around `ast.parse` (`repo_map.py`:178-180).
- [ ] **AC2** The proposed fix lands, pinned by a test: Catch ValueError beside SyntaxError where the source is parsed, and treat it as an unparseable file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
