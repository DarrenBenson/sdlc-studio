# US0473: The in-flight sprint controls are documented as runnable invocations, with coverage derived from the parser and the reference section pinned structurally

> **Status:** Ready
> **Delivers:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, tools/check_budgets.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, tools/tests/test_check_budgets.py, changelog.d/US0473.md
> **Epic:** EP0171
> **Points:** 3

## User Story

**As a** operator reaching for a mid-sprint control
**I want** the batch and appetite verbs documented as invocations I can copy, on the sprint help page and in the sprint reference
**So that** the controls are findable without reading argparse, and a later verb cannot ship undocumented

## Acceptance Criteria

### AC1: AC1: every parser verb is documented as an exact invocation, not as a word that happens to appear

- **Given** the shipped `sprint.py` parser (12 top-level verbs) and its batch action choices
- **When** each verb is looked up in help/sprint.md as the exact invocation string (`sprint batch add`, `sprint batch swap`, `sprint batch add-epic`, `sprint appetite`, and one per top-level verb) constrained to a fenced code block or a table cell
- **Then** the count of documented verbs equals the count of parser verbs, including `goal-review` and `reopen` which are absent from the page today (substring counts on the untouched page: `batch` 23, `plan` 21, `goal-review` 0, `reopen` 0 - a bare substring test passes on a page documenting none of them), and a fixture page carrying the words but not the invocations FAILS the same check inside this test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintInFlightControlDocsTests::test_every_parser_verb_appears_as_an_invocation_and_a_prose_only_page_fails
- **Verified:** yes (2026-08-02)

### AC2: AC2: every documented invocation parses against the shipped parser, over a non-empty extraction

- **Given** help/sprint.md, whose worked examples use the front-door form `/sdlc-studio sprint ...` (the page holds exactly one `sprint.py` mention, at line 185, and it is prose)
- **When** lines matching `/sdlc-studio sprint <verb> ...` where `<verb>` is a parser choice are extracted, the bare-flag front-door form (`/sdlc-studio sprint --crs ...`) is mapped onto `plan`, and each is parsed by `build_parser()`
- **Then** every extracted line parses without SystemExit, and the extracted count is at least the number of verbs this story documents - an empty extraction is RED, not green (the subparser is `required=True`, so an unmapped bare-flag form exits 2)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintInFlightControlDocsTests::test_every_extracted_invocation_parses_and_the_extraction_is_not_empty
- **Verified:** yes (2026-08-02)

### AC3: AC3: the reference gained a named in-flight-control section carrying the same invocations

- **Given** reference-sprint.md, 760 lines and carrying no in-flight-control section before this story
- **When** the file is parsed for a heading named for the in-flight controls and the four invocations are looked up WITHIN that section's body
- **Then** the heading exists and all four invocations appear under it - so the story cannot close with the reference file untouched, which the three-guard shell run alone permits (all three guards exit 0 on the clean tree)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintInFlightControlDocsTests::test_reference_sprint_carries_a_named_in_flight_control_section_with_the_invocations
- **Verified:** yes (2026-08-02)

### AC4: AC4: the line ceiling was raised deliberately in the same commit as the prose

- **Given** reference-sprint.md at 760 lines against a recorded ceiling of 724 with CEILING_TOLERANCE 1.05 (724 x 1.05 = 760.2), so one added line breaks the budget guard
- **When** the recorded ceiling for reference-sprint.md is read from tools/check_budgets.py and compared with the shipped file's line count
- **Then** the ceiling is greater than 724 and the file is within it WITHOUT relying on the 5% tolerance, so the prose and its ceiling land together rather than the prose landing on borrowed headroom
- **Verify:** pytest tools/tests/test_check_budgets.py::ReferenceSprintCeilingTests::test_the_recorded_ceiling_admits_the_shipped_file_without_tolerance
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
