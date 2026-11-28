# BG1788: The 6.5.0 cut's test declares CHANGELOG.md its census subject, so a CHANGELOG-only commit selects unit suites and the push gate's selection test is red

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_release_cut_v65.py
> **Evidence:** Run twenty-eight's fifth push of main (2026-11-28, about 06:46Z): devserver1 refused b5fd073af at the push boundary, full-suite 1 red: `tools/tests/test_precommit_selection.py`::SkipTests::`test_changelog_skips`; reproduced locally at the same commit.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T06:49:47Z

## Summary

US1330's new test module, `tools/tests/test_lean_release_cut_v65.py`, opens with `# test-census-subject: CHANGELOG.md`. `gate.py --suite-decision` therefore selects it, and with it `test_root_census`, `test_doc_claims` and two others, for a commit that changes CHANGELOG.md alone. US0220's pinned rule says such a commit runs no unit suite: `tools/tests/test_precommit_selection.py`::SkipTests::`test_changelog_skips` fails at f2440fd9b, and the push boundary's full suite refused b5fd073af on that one test (10938 passed, 1 failed). The 6.4.0 cut's test (`test_lean_release_cut_v64.py`) declares no census subject, and the push's full suite still runs the cut test.

## Steps to Reproduce

1. At f2440fd9b, run `python3 .claude/skills/sdlc-studio/scripts/gate.py --root . --suite-decision --changed CHANGELOG.md`.
2. It prints `suite-mode: selected` and names tools/tests/test_lean_release_cut_v65.py among its selectors.
3. `python3 -m pytest tools/tests/test_precommit_selection.py -k test_changelog_skips` fails: True is not false.

## Proposed Fix

Remove the `# test-census-subject: CHANGELOG.md` header from `tools/tests/test_lean_release_cut_v65.py`, as the 6.4.0 cut's test carries none, so a CHANGELOG-only commit selects no unit suite again and the cut test runs in the push's full suite.

## Acceptance Criteria

- [ ] **AC1** A commit that changes CHANGELOG.md alone selects no unit suite beyond the sweeps every commit runs, as US0220 pins.
  - **Verify:** pytest tools/tests/test_precommit_selection.py::SkipTests::test_changelog_skips
- [ ] **AC2** The 6.5.0 cut's test module still passes, and still runs in the push's full suite.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v65.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
