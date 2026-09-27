# BG0801: The known-issues page puts its ship-open paragraph under the oldest bar's history and states a Not carried count the corpus contradicts

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, changelog.d/BG0801.md
> **Severity:** Medium
> **Points:** 2

## Summary

`tools/known_issues.py` renders the 'Medium and Low findings ship open ... triaged to v6.1' paragraph after the last history heading, so it reads as part of 'The bar v5.0.0 was held to'; and its fixed TAIL says 'Three High findings were ruled Won't Fix ... and one was superseded', where the corpus at f76b70cc holds four High findings at Won't Fix (BG0124, BG0139, BG0583, BG0713) and none superseded. The v6.0.0 cut writes this page; a disclosure with a false count is not current.

## Steps to Reproduce

python3 tools/`known_issues.py` write --release 6.0.0 in a scratch clone; read the section order and the Not carried sentence; count High findings at Won't Fix/Superseded in sdlc-studio/bugs.

## Proposed Fix

Emit the ship-open paragraph under the bar in force, before the history; derive Not carried from the corpus (High/Critical findings at a non-fixed terminal status, by id), or cut the section.

## Acceptance Criteria

- [ ] **AC1** Given `known_issues.py write --release 6.0.0` over a corpus with open Medium findings, when the page is rendered, then the ship-open paragraph sits under `## The bar v6.0 is held to`, before the first `kept as history` heading. Fails on: HEAD, where it follows `## The bar v5.0.0 was held to, kept as history`
  - **Verify:** pytest tools/tests/test_known_issues.py::PageProseTests::test_the_ship_open_paragraph_sits_under_the_bar_in_force
- [ ] **AC2** Given a corpus holding four High findings at Won't Fix and none superseded, when the page is rendered, then Not carried states four and names each id, and a corpus with none renders no such claim. Fails on: HEAD's constant 'Three ... and one was superseded'
  - **Verify:** pytest tools/tests/test_known_issues.py::PageProseTests::test_not_carried_is_derived_from_the_corpus

## Notes

Release-bar blocker (the page must be true at the tag). Carries the Sprint 5 polish note on US0946 ('Not carried still v5 wording'). Ratchet: none.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0801) |
