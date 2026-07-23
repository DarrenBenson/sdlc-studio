# US0374: critic correct supersedes a verdict row with an authorised reason, the author alone refused

> **Status:** Draft
> **Delivers:** CR0372
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0133
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, sdlc-studio/reviews/critic-verdicts.md

## User Story

**As an** operator holding an append-only review log that recorded an event which did not happen
**I want** a `critic supersede` command that retires the wrong row against a stated reason and a named authoriser
**So that** the correction is made through the tool with its provenance on the record, rather than by hand-editing the one file whose value is that nobody edits it

## Acceptance Criteria

### AC1: a supersession is recorded against a reason and an authoriser, and the original row is left in place

- **Given** a `critic-verdicts.md` carrying an APPROVE row for `US0276` naming `Darren Benson (operator)` as reviewer with author `sdlc-studio; agent; v1`
- **When** `critic supersede` is run for that unit and row, with a reason and an `--authorised-by` who is not the row's author
- **Then** an appended supersession record names the unit, the row it retires, the reason and the authoriser, and the verdict row itself is still present byte-for-byte in `critic-verdicts.md` - the log is corrected by addition, never by deletion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersedeTests::test_supersession_records_reason_and_authoriser_and_leaves_the_row

### AC2: the row's own author cannot supersede it alone

- **Given** the same wrong row, authored by `sdlc-studio; agent; v1`
- **When** a supersession is attempted with `--authorised-by` naming that same author, or with no authoriser at all
- **Then** `record_supersession` refuses loudly and writes nothing, so the party who wrote the wrong row cannot quietly retire it on its own say-so
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersedeTests::test_row_author_alone_is_refused_as_the_authoriser

### AC3: a supersession naming no real row is refused

- **Given** a verdicts log with no row for `US9999`, and one whose `US0276` row carries a different date to the one named
- **When** a supersession is attempted against either
- **Then** it is refused naming what was not found, and no supersession record is written - a correction that points at nothing is a false erratum, and the CLI exits 2
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersedeTests::test_unmatched_row_refused_and_nothing_written

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: `supersede`/`correct` verb, appended record, author-alone and unmatched-row refusals; TDD red-first, mutation-proven |
