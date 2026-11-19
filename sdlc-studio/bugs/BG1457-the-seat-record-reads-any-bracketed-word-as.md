# BG1457: The seat record reads any bracketed word as a seat, lane brief --seat accepts any value, and retro seats counts rounds across deliveries

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_seat_record_edges.py, changelog.d/BG1457.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run thirteen (RUN-01M7EYR3) reviews: sdlc-studio/reviews/verdicts/US1061/e6aa7796c870-de0ae7a6.txt and sdlc-studio/reviews/verdicts/US1062/d61be0d3a16a-c6e88f35.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T08:19:09Z

## Summary

Run thirteen's US1061 and US1062 reviews (APPROVE, non-blocking): `critic.recorded_seat` treats any parenthesised word as a seat, so an author such as 'Claude Opus 5.5 (builder)' raises no warning and `retro.py seats` lists a seat called builder the project does not declare (seen on RETRO0144); `sprint lane brief --seat` accepts any value ('QA', 'bogus') unchecked; and `retro seats` numbers rounds across every delivery a unit has had rather than per delivery as `critic.delivery_rounds` does. Five behaviours the reviewer named have no pinning test.

## Steps to Reproduce

Record a verdict whose author is 'Claude Opus 5.5 (builder)' and run `retro.py seats`: a seat 'builder' is listed and no warning was raised. Run `sprint lane brief --units X --seat bogus`: accepted.

## Proposed Fix

Read a seat only from the project's declared seats (`persona_resolve)`; refuse an undeclared `--seat`; number rounds per delivery through critic's public round reader; pin the five behaviours.

## Acceptance Criteria

- [ ] **AC1** Given an author whose bracketed word is not a declared seat, when the verdict is recorded and seats are scored, then a warning names it and no seat of that name is listed. Fails on: 'builder' scored as a seat.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_record_edges.py::SeatRecordEdgeTests
- [ ] **AC2** Given `lane brief --seat` naming an undeclared seat, when it runs, then it refuses naming the declared seats. Fails on: acceptance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
