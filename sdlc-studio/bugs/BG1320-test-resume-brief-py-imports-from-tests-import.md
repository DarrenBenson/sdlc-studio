# BG1320: `test_resume_brief.py` imports `from tests import quiet`, which resolves to `tools/tests` when a run collects it with a repository-tooling test, so the commit hook and the push gate error on collection

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, changelog.d/BG1320.md
> **Evidence:** US1145's refused landing (RUN-01M7061X, land-US1145.log): ImportError collecting test_resume_brief.py
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:15:55Z

## Summary

Found landing US1145 in run nine (2026-11-09). US1140 added `.claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py` with `from tests import quiet` (line 26). Every other skill test imports the helper as `import quiet` with the tests directory on sys.path. When one pytest run collects this module together with a `tools/tests` module, the `tests` package is `tools/tests`, which has no `quiet`, and collection errors: US1145's landing commit was refused with 1776 passed and 1 error. The push gate runs the whole suite in one session, so the next push fails the same way.

## Steps to Reproduce

1. From the repository root, run `python3 -m pytest tools/tests/test_persona_coherence.py .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py -q`.
2. Collection of `test_resume_brief.py` errors: cannot import name 'quiet' from 'tests' (tools/tests/`__init__.py).`

## Proposed Fix

Import the helper the way every other skill test does (`import quiet` with the tests directory on sys.path), and add a test that collects `test_resume_brief.py` in one pytest session beside a tools/tests module.

## Acceptance Criteria

- [ ] **AC1** Given one pytest session that collects `tools/tests/test_persona_coherence.py` and `.claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py` together, then both collect and pass, with no ImportError for `quiet`. Fails on: `from tests import quiet` left in test_resume_brief.py.
  - **Verify:** shell python3 -m pytest tools/tests/test_persona_coherence.py .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py -q -p no:cacheprovider
  - **Verified:** yes (2026-11-09)
- [ ] **AC2** Given `test_resume_brief.py`, then it imports the console-diagnostics helper the way the other skill tests do (`import quiet` with its own tests directory on sys.path), and its own tests still pass alone. Fails on: a `from tests import` of any helper in the module.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py
  - **Verified:** yes (2026-11-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-09 | Claude Opus 5.5 (run nine, D0451) | Criteria and Verify lines authored when BG1320 joined the run |
