# BG0757: repo_map.py build crashes on Python 3.10 when a source file holds a null byte

> **Status:** Fixed
> **Verification depth:** functional (a real null byte under python3.10: repo_map.py build exits 1 at HEAD and 0 with the fix, both files indexed; three mutants killed by the QA reviewer)
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_map_null_byte.py, changelog.d/BG0757.md
> **Evidence:** US0908 review round 1, RUN-01M39MC0: the whole skill suite run under a 3.10 venv
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repo_map.py` catches only SyntaxError around `ast.parse` (`repo_map.py`:178-180). Python 3.10 raises ValueError for a source string containing a null byte, so `repo_map.py build` exits 1 with 'source code string cannot contain null bytes' on 3.10, where 3.11+ raise SyntaxError and the build continues. `test_repo_map.py`::BuildRobustnessTests::`test_binary_garbage_in_source_does_not_crash` fails under 3.10. The skill declares 3.10 as its floor, so consumers on 3.10 hit it.

Out of scope, noted: `command_audit.py`:654 and `verify_ac.py`:4372 also catch only SyntaxError around `ast.parse`. They parse this skill's own scripts and a project's test files rather than arbitrary consumer source, so they are not in this fix.

## Steps to Reproduce

1. Put a .py file containing a null byte in a fixture repository. 2. Run `python3.10 .claude/skills/sdlc-studio/scripts/repo_map.py build` against it. 3. It exits 1; under 3.12 it exits 0.

Re-run at 65cdf1ca on 2026-09-25: `python3.10 repo_map.py build --root <fixture>` exits 1 with `error: source code string cannot contain null bytes`; `python3` (3.14) exits 0 with `indexed 2 files`.

## Proposed Fix

Catch ValueError beside SyntaxError where the source is parsed, and treat it as an unparseable file.

## Acceptance Criteria

- [ ] **AC1** Given `parse_python` over source for which `ast.parse` raises ValueError (patched in the test, so it fails the same way on every interpreter, as 3.10 does for a null byte), when it runs, then it returns the regex fallback's symbols and imports for that source rather than raising. Fails on: HEAD's `except SyntaxError` alone; catching ValueError but returning no symbols, which drops the file from the map.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_map_null_byte.py::NullByteTests::test_a_valueerror_from_the_parser_falls_back_to_the_regex_index
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a fixture repository holding one .py file with a null byte and one clean file, when `repo_map.py build --root <fixture>` runs through its CLI with `ast.parse` raising ValueError for the null-byte source, then it exits 0 and indexes both files. Fails on: HEAD, which exits 1 (measured under python3.10); a guard that skips any file containing a null byte before parsing, which exits 0 but indexes only the clean file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_map_null_byte.py::NullByteTests::test_the_build_cli_exits_zero_over_a_null_byte_file
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (python3.10 build exits 1 on a null byte, 3.14 exits 0); criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module that inject the 3.10 ValueError, so they fail on any interpreter; each names the wrong fix it fails on; 1 point stands |
