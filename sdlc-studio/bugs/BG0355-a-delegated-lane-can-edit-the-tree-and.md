# BG0355: A delegated lane can edit the tree and stop without returning a result, leaving finished work unrecorded

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; predicates mutation-killed)
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-agentic-lessons.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Observed four times tonight. A lane that dies mid-flight leaves real code in the working tree behind a unit still marked Ready, and a restart cannot tell a delivered unit from an untouched one because the revision row is written before the work. One restarted lane was dispatched onto three units whose repair was already present, with no signal. A partial edit also reached a commit this way in the previous sprint.

## Steps to Reproduce

ls -la --time-style=full-iso tools/test_census.py tools/tests/test_test_census.py -> both 2026-07-28 00:55-00:56, untracked (git log -- tools/test_census.py empty); sdlc-studio/stories/US0506-*.md and US0507-*.md both; ls -la --time-style=full-iso on the three stories: 2026-07-28 00:47:35 US0480-..., 2026-07-28 00:47:41 US0461-..., 2026-07-28 00:48:08 US0482-..., against session start Tue Jul 28 01:25:24 AM BST 2026. US0480 a; /home/darren/code/DarrenBenson/sdlc-studio/sdlc-studio/bugs/BG0348-an-all-skipped-run-is-still-stamped-green.md line 3 '> **Status:** Open' beside line 85 '| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteri; mtimes: .claude/skills/sdlc-studio/scripts/reconcile.py 2026-07-28 00:46:32, scripts/init.py 00:50:55, scripts/tests/test_init.py 00:50:45, against bug artefacts last written 2026-07-27 12:38 and still 'Status: Open' wit

## Proposed Fix

See the summary; each cited site names its own remedy.

## Acceptance Criteria

### AC1: A briefed unit is marked in flight, and the marker outlives the process that set it

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests::test_a_dispatch_that_never_returned_survives_to_be_reported
- **Verified:** yes (2026-07-28)

### AC2: A returned unit is cleared whatever the outcome, so the warning does not fire on everything

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests::test_a_returned_unit_is_cleared_whatever_the_outcome
- **Verified:** yes (2026-07-28)

### AC3: The whole in-flight contract holds, including re-dispatch and no open run

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. |
