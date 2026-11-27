# US1345: critic.py approach brief prints a seat's review of the approach note, and the code review brief carries none of it

> **Status:** Ready
> **Risk-class:** high
> **Delivers:** CR0756
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_brief.py, changelog.d/US1345.md
> **Epic:** EP0385
> **Points:** 3
> **Depends on:** US1344
> **Persona:** Abena Osei

## User Story

**As** the seat reviewing a builder's approach, **I want** one brief holding my render, the
unit's criteria, its binding decisions and the note, **so that** I judge the plan against the
same law the code will be judged by, and the code reviewer stays unanchored.

## Acceptance Criteria

### AC1: the brief holds what the seat judges against

- **Given** a story with two criteria, a decision id named in its Notes, a complete note, and a
  project seat card for engineering
- **When** `critic.py approach brief --unit <id> --seat engineering --note <path>` is run
- **Then** stdout carries the card's review render path, both criteria verbatim, the decision's
  id and its text from `sdlc-studio/decisions.md`, the note verbatim, the instruction to
  spot-check by execution in a scratch copy only, the statement that this seat will not review
  the code, and a record footer naming `critic.py approach record` with the unit, both verdicts
  and the note path. Fails on: HEAD, where `critic.py approach` is an invalid choice.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_brief.py::SolutionReviewBriefTests::test_the_brief_holds_what_the_seat_judges_against

### AC2: an incomplete note is refused before any brief

- **Given** the same story and three notes: one missing the `## May break` heading, one whose
  `## Tests` section names a test for AC1 only, and a complete one
- **When** `approach brief` is run on each
- **Then** the first two exit 2, naming the missing heading or the criterion id with no test,
  with nothing on stdout, and the complete note prints its brief (the control). Fails on: HEAD,
  which has no such verb.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_brief.py::SolutionReviewBriefTests::test_an_incomplete_note_is_refused_before_any_brief

### AC3: the code review brief carries none of the solution review

- **Given** the story with a GO recorded by the engineering seat through `approach record`
- **When** `critic.py brief --unit <id> --seat qa` and `critic.py brief --unit <id> --seat
  engineering` are run, first round and with `--rejoinder`
- **Then** no stdout carries the note's path, any line of its text, the verdict or the approach
  reviewer's name, and only the engineering brief says on stderr that the code reviewer must be a
  fresh context that has not read the note. Fails on: HEAD, where no GO can be recorded and
  `critic.py brief` says nothing of a solution review on either stream.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_brief.py::SolutionReviewBriefTests::test_the_code_review_brief_carries_none_of_the_solution_review

### AC4: the runbook and the catalogue name both commands

- **Given** reference-sprint-toolchain.md section 3 and reference-scripts-review.md's critic.py
  entry
- **When** they are read
- **Then** section 3 has a row "Review a builder's approach" whose command names `critic.py
  approach brief` and `critic.py approach record`, after "Build a unit", with the table's three
  columns unchanged, and the catalogue entry names both verbs and the ledger. Fails on: HEAD,
  where both pages have 0 mentions of an approach or a solution review.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_brief.py::SolutionReviewBriefTests::test_the_runbook_and_the_catalogue_name_both_commands

## Notes

- Ran: the invalid-choice probe; a delivery verdict recorded under an approach-named reviewer at
  HEAD (exit 0) and the QA brief that land wrote, whose only "approach" hits were the fixture
  path (Evidence S2).
- AC3's exclusion half holds at HEAD only because nothing exists to leak; it is a pin against a
  future leak. Its failing half is the stderr line.
- Binding decisions are found by id only (a `D` plus four digits in the unit, its epic and its
  delivering request); a decision that binds by subject without being named is not found. Say so
  in the brief's own text.
- Reuse `_brief`'s criteria and seat-render machinery; do not route through `--phase`, which
  `critic.py record` refuses as the retired plan phase.
- Beside the existing tests: reference-sprint-toolchain.md is read by 9 modules.
  test_lane_builder_brief.BuilderRunbookTests holds section 3 to one table with columns Do,
  Command, Instead of and requires its three DELIVER_ROWS by exact cells (assertIn, so a new row
  is allowed); test_lane_land holds the land row to "removes the worktree" (S4 keeps it);
  test_wave_boundary_docs reads the handoff rows. The runbook is within budget (115 lines).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
