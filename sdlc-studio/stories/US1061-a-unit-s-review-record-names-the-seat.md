# US1061: A unit's review record names the seat that built it, so an author's repairs can be scored

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py, changelog.d/US1061.md
> **Epic:** EP0287
> **Points:** 2
> **Depends on:** US1030, US1011
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose engineering seat once took four review rounds to model one race
**I want** `sprint lane brief` to name the seat it frames to build a unit, the review brief's record command to carry that seat as `--author "<holder> (<role>)"`, and `critic.py record` to warn when an author names no seat
**So that** the learning loop can score an author's repairs, rounds to converge included, and not only the reviewers' verdicts

## Acceptance Criteria

- **AC1:** Given a project whose engineering card is held by Dani Okafor and whose qa card by Sam Eriksson, when `sprint.py lane brief --units US0001` runs and then `critic.py brief --unit US0001 --seat product` runs, then the lane brief names Dani Okafor (engineering) as the building seat and the review footer's record command carries `--author "Dani Okafor (engineering)"`, and after `lane brief --units US0002 --seat qa` the footer for US0002 carries `--author "Sam Eriksson (qa)"`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_the_record_command_names_the_seat_that_built_the_unit
- **AC2:** Given a project that declares seats, when `critic.py record --unit US0001 --verdict APPROVE --reviewer "Lena Marsh (product)" --author "engineering-seat build worker"` runs, then the row is written and stderr names the `<holder> (<role>)` form the author lacks, and with `--author "Dani Okafor (engineering)"` nothing is printed about the author.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_a_seatless_author_is_named_and_recorded

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the footer prints a fixed author or none, or the lane's seat is never recorded so the footer cannot tell a QA-built unit from an engineering one
- AC2 must fail on: the author's seat read by `seat_for`'s name heuristic rather than the `(role)` group, so a seatless author passes silently
- Serves: Maya Okafor #3.
- D0364 ruling 2. Checked at HEAD: no Author cell among 1,552 ledger rows carries a `(role)` group (BG0993's reads `engineering-seat-triage`), and `lane_brief_text` (sprint.py:2704) names no seat.
- Adds the public helper `critic.recorded_seat(cell)`: the first `(<role>)` or `(<role> seat)` group, US1032's lane rule. The warning, the persona review record and the seat record read it (LL0016); US1032 (later) reuses it.
- `sprint lane brief --seat <role>` (default engineering) records the seat on the lane start (`run_state.record_lane_start`). With no lane record for the unit, the footer prints the build seat's holder as engineering and one stderr line saying no lane recorded the builder.
- The warning sits in `_write_verdict`, so `transition set --verdict` and `artifact.py close --verdict` get it too; it never refuses (LL0056).
- Builds after US1030 and US1011, which rewrite the same footer lines; about 2 points as the operator sized it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
