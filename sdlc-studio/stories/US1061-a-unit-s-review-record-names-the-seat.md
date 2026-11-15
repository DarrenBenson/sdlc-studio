# US1061: A unit's review record names the seat that built it, so an author's repairs can be scored

> **Status:** Done
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, changelog.d/US1061.md
> **Epic:** EP0287
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, whose engineering seat once took four review rounds to model one race
**I want** `sprint lane brief` to name the seat it frames to build a unit, the review brief's record command to carry that seat as `--author "<holder> (<role>)"`, and `critic.py record` to warn when an author names no seat
**So that** the learning loop can score an author's repairs, rounds to converge included, and not only the reviewers' verdicts

## Acceptance Criteria

- **AC1:** Given a project whose engineering card is held by Dani Okafor and whose qa card by Sam Eriksson, when `sprint.py lane brief --units US0001` runs and then `critic.py brief --unit US0001 --seat product` runs, then the lane brief names Dani Okafor (engineering) as the building seat and the review footer's record command carries `--author "Dani Okafor (engineering)"`, and after `lane brief --units US0002 --seat qa` the footer for US0002 carries `--author "Sam Eriksson (qa)"`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_the_record_command_names_the_seat_that_built_the_unit
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a project that declares seats, when `critic.py record --unit US0001 --verdict APPROVE --reviewer "Lena Marsh (product)" --author "engineering-seat build worker"` runs, then the row is written and stderr names the `<holder> (<role>)` form the author lacks, and with `--author "Dani Okafor (engineering)"` nothing is printed about the author.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_a_seatless_author_is_named_and_recorded
  - **Verified:** yes (2026-11-15)
- **AC3:** Given a brief for `--seat qa` on a project where qa's card is held by Sam Eriksson, when `critic.py brief --unit US0001 --seat qa` runs, then the footer's record command carries `--reviewer "Sam Eriksson (qa)"` (the US1030 AC3 shape), and with an explicit `--seat engineering` it carries the engineering holder, so a recorded Reviewer cell always names its seat in the form `critic.recorded_seat` reads.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_the_footer_names_the_seat_as_reviewer
  - **Verified:** yes (2026-11-15)

## Notes

- Run thirteen grooming (D0479):
  - AC1 must fail on: the footer prints a fixed author or none, or the lane's seat is never recorded
  - AC2 must fail on: the author's seat read by `seat_for's` name heuristic instead of the (role) group, so a seatless author passes silently
  - AC3 must fail on: the footer omits --reviewer or writes the role in free text, so retro.py seats (US1062) reads every new row as naming no seat
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 2 (an accountable person: the author and reviewer seat are named on every row).
  - Points 2 -> 3: AC3 absorbs US1030 AC3 (footer --reviewer), the only part of US1030 that US1062 truly needs. US1030's derived-seat AC1/AC2 and US1029 (critic.py seats, Draft) are not needed; both stay out of the run. Dependency on US1030 is therefore broken; US1011 is Done.
  - Footer is built by `critic._record_footer` (critic.py ~4579) and is pinned by five existing tests, now in Affects. `critic.recorded_seat(cell)` is the public helper this story creates; US1062 reuses it (LL0016).
  - Before build: re-read the five footer tests; the footer string changes in every one of them.
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the footer prints a fixed author or none, or the lane's seat is never recorded so the footer cannot tell a QA-built unit from an engineering one
- AC2 must fail on: the author's seat read by `seat_for`'s name heuristic rather than the `(role)` group, so a seatless author passes silently
- Serves: Maya Okafor #3.
- D0364 ruling 2. Checked at HEAD: no Author cell among 1,552 ledger rows carries a `(role)` group (BG0993's reads `engineering-seat-triage`), and `lane_brief_text` (sprint.py:2704) names no seat.
- Adds the public helper `critic.recorded_seat(cell)`: the first `(<role>)` or `(<role> seat)` group, US1032's lane rule. The warning, the persona review record and the seat record read it (LL0016); US1032 (later) reuses it.
- `sprint lane brief --seat <role>` (default engineering) records the seat on the lane start (`run_state.record_lane_start`). With no lane record for the unit, the footer prints the build seat's holder as engineering and one stderr line saying no lane recorded the builder.
- The warning sits in `_write_verdict`, so `transition set --verdict` and `artifact.py close --verdict` get it too; it never refuses (LL0056).
- Builds after US1030 and US1011, which rewrite the same footer lines; about 2 points as the operator sized it.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1030 and US1011 (Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, criteria rewritten to four or fewer, notes, Points 2 to 3 (absorbs US1030's footer criterion) |
