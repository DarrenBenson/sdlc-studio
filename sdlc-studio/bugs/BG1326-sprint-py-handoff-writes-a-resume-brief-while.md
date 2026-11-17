# BG1326: `sprint.py handoff` writes a resume brief while a lane is still in flight, so the wave boundary reference-sprint.md defines is stated but not enforced, and four files still say no command writes a handoff

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/help/handoff.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py
> **Evidence:** US1142-verdict-r1 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:03:27Z

## Summary

From US1142's QA review (qa-seat-US1142-r1, non-blocking, 2026-11-09). US1142 defines a wave boundary (every lane of the wave accepted, none in flight) as the point a session hands off, and US1140's `resume_brief.at_wave_boundary` computes it, but `sprint.py handoff` (US1141) writes the brief whatever the boundary says. Four files outside US1142's Affects still say 'No command writes a handoff' and do not mention the resume brief.

## Steps to Reproduce

1. Open a run with a lane in flight and run `sprint.py handoff`: it writes the brief without naming the in-flight lane as a reason to wait.
2. Grep the skill for 'No command writes a handoff': four files still say it.

## Proposed Fix

Have `sprint.py handoff` refuse (or, under a flag, warn) when `at_wave_boundary` is false, naming the blocking unit; correct the four stale sentences to name `sprint.py handoff` and the resume brief; pin both.

## Acceptance Criteria

- [ ] **AC1** Given an open run with a lane in flight, when `sprint.py handoff` is run, then it exits 2 naming the unit that holds the wave open and its state, and writes no brief; at a wave boundary it writes the brief as before. Fails on: a brief written mid-wave with nothing said.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HandoffCliTests::test_handoff_off_a_wave_boundary_is_refused_naming_the_blocking_unit
- [ ] **AC2** Given the same run, when `sprint.py handoff` is run with its flag for handing off away from a boundary, then it writes the brief and warns on stderr naming the blocking unit. Fails on: no route for a session that must stop mid-wave, or an override that says nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HandoffCliTests::test_the_off_boundary_flag_writes_the_brief_and_warns
- [ ] **AC3** Given `help/handoff.md`, `reference-scripts-domain.md` and `handoff.py`'s docstring and parser description, when each sentence saying no command writes a handoff is read, then it names `sprint.py handoff` and the resume brief beside the retired handoff record. Fails on: a page telling a reader nothing writes a handoff while `sprint.py handoff` does.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_no_page_says_no_command_writes_a_handoff_without_naming_the_resume_brief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
