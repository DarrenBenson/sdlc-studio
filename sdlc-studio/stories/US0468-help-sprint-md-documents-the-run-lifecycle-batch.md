# US0468: help/sprint.md documents the run lifecycle - batch mutation, stop, appetite and rolling - bound in invocation form to the shipped parser and the run record

> **Status:** Ready
> **Delivers:** CR0442
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/fixtures/sprint-help-pre-rewrite.md
> **Epic:** EP0170
> **Points:** 5

## User Story

**As a** operator or agent whose sprint has met reality mid-run
**I want** the sprint help page to cover living with a run, not only planning and closing one
**So that** a batch is adjusted through the shipped verbs rather than by hand-editing state or not at all

## Acceptance Criteria

### AC1: every shipped verb is documented in invocation form, and the check goes red on the page as it stands

- **Given** the 12 verbs derived from sprint.py's build_parser subparser tree (plan, breakdown, close, boundary, report, preflight, goal-verdict, goal-review, reopen, stop, decision, batch), and a committed fixture copy of the page as it is before the rewrite
- **When** each verb is required in invocation form - /sdlc-studio sprint <verb> or sprint.py <verb> - rather than as a bare substring, and each run-lifecycle verb (batch, stop, reopen, boundary) is additionally required to have its own heading
- **Then** every verb matches on the rewritten page, the derived verb set is asserted non-empty, and the SAME check run over the pre-rewrite fixture FAILS naming batch, stop, reopen, preflight, breakdown, goal-verdict and goal-review - proving it discriminates, because a substring match passes today on stop (8 occurrences), batch (23) and report (13) while none of the three is documented as a verb
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_every_shipped_verb_appears_in_invocation_form_and_the_pre_rewrite_page_fails
- **Verified:** yes (2026-08-05)

### AC2: the batch-mutation and stop sections are bound to what the run record does

- **Given** the facts lib/run_state.py owns: the batch_changes entry keys written by a real drop and add against a temp run, the RunStateError raised on a blank reason (run_state.py:697), the drop-versus-Deferred distinction (a drop removes the unit from `batch` and leaves its status untouched, whereas Deferred keeps its place and still blocks the close), and stop's refusal while any unit the pending question does not block remains, with --force recording what could have proceeded
- **When** the page's batch-mutation and stop sections are compared with those, the keys read from the record the module actually writes and the required --reason read from the `batch` subparser rather than named in the test
- **Then** the sections name every batch_changes key, state that a drop needs a reason and is recorded, state that a drop is NOT Deferred and why, and state stop's refusal condition and what --force puts on the record; a key added or renamed in batch_changes fails the test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_batch_and_stop_sections_name_every_recorded_key_and_the_drop_versus_deferred_rule
- **Verified:** yes (2026-08-05)

### AC3: no documented invocation is fictional, in either class

- **Given** every /sdlc-studio sprint example on the page, partitioned into verb-first examples and the flag-first slash examples (lines 15-20 and 34-42 today: --bugs/--crs/--epic/--order/--autonomous), which are plan-shaped and belong to the `plan` subparser, not the top-level one
- **When** verb-first examples are parsed against build_parser, flag-first examples against the `plan` subparser, and any flag no parser owns is looked for in help/arguments.md
- **Then** each parses or resolves; a flag owned by neither a parser nor the argument reference fails. --autonomous is the live case: it is on NO sprint.py parser and absent from help/arguments.md, resting only on reference-sprint.md's Autonomous mode section, so this story gives it its help/arguments.md row rather than leaving a flag the page's own table documents unlisted in the argument reference. The test asserts a non-zero parsed count in EACH class, so an over-tight filter cannot report coverage it never achieved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_every_documented_invocation_resolves_across_verb_first_and_flag_first_classes
- **Verified:** yes (2026-08-05)

### AC4: the appetite and rolling sections name every field and flag the code owns

- **Given** the appetite record run_state.appetite_record writes (units, minutes, standing_units, standing_minutes, over_appetite), the plan flags that set it (--appetite-minutes, --appetite-units) and the rolling flags (--cycles, --stop-on) plus the boundary verb - all read from the parser and the record, never listed in the test
- **When** the page's appetite and rolling sections are checked for each of them
- **Then** the appetite section names every recorded key and both flags, states what the appetite bounds, where it is set, and that it is fixed once the plan is written until CR0441 changes that; the rolling section names both rolling flags and the boundary verb and states that a rolling run regenerates the plan at each boundary rather than queueing plans, so a reader looking for a sprint queue finds the current answer and the reason; a key or flag added or renamed fails
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_appetite_and_rolling_sections_name_every_recorded_field_and_flag
- **Verified:** yes (2026-08-05)

### AC5: the binder fails loud rather than passing vacuously

- **Given** fixture pages that are missing, empty, or have lost the section a check reads
- **When** the surface binder runs over each
- **Then** it fails naming what it could not read and never reports coverage from a page it did not find; and on the real page every check asserts its matched-item count is non-zero, so an absent page and a page with nothing wrong in it can never read the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintSurfaceTests::test_binder_fails_loud_when_the_page_or_section_is_missing
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
