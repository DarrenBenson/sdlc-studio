# BG1238: Run seven's landed units leave the push gate red: reference-sprint.md is over its ceiling and two environment-scrub sites are unregistered

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, tools/tests/test_skill_tests_env.py, tools/check_budgets.py, tools/tests/test_check_budgets.py, changelog.d/BG1238.md
> **Evidence:** run seven (RUN-01M6RAP7) push of 4950f968, refused at the push boundary by devserver1's full suite, 2026-11-06
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:27:11Z

## Summary

The push of 4950f968 was refused by the full suite on devserver1 (3 failed, 8584 passed): `tools/tests/test_check_budgets.py` holds `reference-sprint.md` to its 859-line ceiling without tolerance, and run seven's meter and cost sections (US1124, US0987, US1127, US0988, US1123) took it to 900 lines; `tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests::test_every_scrub_site_is_registered` finds two unregistered sites that scrub the git environment, `lib/lanes.py` (US1126) and `tools/bench/runner.py` (US1128). The commit hook allows +5% and selects neither test, so each unit committed green.

## Steps to Reproduce

Run `python3 -m pytest tools/tests/test_check_budgets.py tools/tests/test_skill_tests_env.py -q` on main at 4950f968 or later.

## Proposed Fix

Bring `reference-sprint.md` to its ceiling by tightening or moving prose (the per-harness Token meters paragraphs are the candidates), never by raising the ceiling unless nothing can move, and then only with a rationale; register both scrub sites in `SCRUB_SITES` with what pins each.

## Acceptance Criteria

- [ ] **AC1** `reference-sprint.md` fits its recorded ceiling without the tolerance, and the ceiling is not what was raised to fit it.
  - **Verify:** pytest tools/tests/test_check_budgets.py::ReferenceSprintCeilingTests
  - **Verified:** yes (2026-11-06)
- [ ] **AC2** Every site that scrubs the git environment, `lib/lanes.py` and `tools/bench/runner.py` included, is registered with what pins it, and the registry has no rotted entry.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored with Verify checks for run seven |
