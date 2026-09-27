# BG0802: artifact new --type bug drops its --verify line and writes an unnamed criterion, so sprint plan refuses the bug it just filed

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG0802.md
> **Severity:** Medium
> **Points:** 1

## Summary

On a fresh rc.1 project, `artifact.py new --type bug --ac 'Given x, when y, then z. Fails on: w' --verify 'pytest tests/test_a.py'` exits 0 and writes `- [ ] Given x, ...` with no `**AC1**` and no `Verify:` line; `sprint plan` then refuses the bug as carrying no executable Verify. The help says `--verify` is for stories only, but the value is accepted and discarded (LL0008).

## Steps to Reproduce

init run; artifact.py new --type bug --title t --severity Low --summary s --steps s --fix f --points 1 --affects src/a.py --ac '...' --verify 'pytest tests/`test_a.py`'; read the Acceptance Criteria section.

## Proposed Fix

Pair --ac/--verify for bugs as for stories, in the bug criterion shape (`- [ ] **AC1** ...` with `- **Verify:** ...`); or refuse a --verify the type cannot carry, exit 2, naming the route. Never exit 0 having dropped it.

## Acceptance Criteria

- [ ] **AC1** Given `artifact.py new --type bug` with one `--ac` and one `--verify`, when it writes the bug, then its criterion reads `- [ ] **AC1** <text>` followed by `- **Verify:** <verify>`, and `sprint.py plan` over that bug does not refuse it for a missing Verify. Fails on: HEAD (Verify dropped, criterion unnamed, measured 2026-09-27); writing the Verify under an unnamed bullet the runner cannot pair
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::BugCriteriaTests::test_a_bug_s_verify_is_written_under_its_named_criterion

## Notes

First-week: a user's first filed bug cannot be planned. Found by the QA triage fork and confirmed by the QA seat on a fresh project.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0802) |
