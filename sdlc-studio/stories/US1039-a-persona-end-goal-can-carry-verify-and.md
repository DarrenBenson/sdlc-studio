# US1039: A persona End goal can carry Verify and Applies-to lines, and validate personas checks them

> **Status:** Draft
> **Delivers:** CR0621
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/personas/persona-template.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py, changelog.d/US1039.md
> **Epic:** EP0285
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, a founder-engineer whose product serves people beyond herself
**I want** to give a persona's End goal a Verify line, and the files it constrains as Applies-to patterns, and have validate personas check both
**So that** a goal I mean to check is written in a form the tooling can read, and a pattern that would match nothing is named rather than silently ignored

## Acceptance Criteria

- **AC1:** Given a persona card whose End goal 1 carries an unfilled `{{...}}` Verify, End goal 2 a Verify `verify_ac` lint flags (`npm test`), End goal 3 a well-formed Verify, and a `- **Verify:**` line under its Scenario, when `validate.py personas` runs, then it warns `persona-goal-verify` for End goals 1 and 2 by card and number, and not for End goal 3 or the Scenario line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::GoalVerifyLintTests::test_validate_personas_lints_each_end_goal_verify
- **AC2:** Given End goals carrying `Applies-to: ha/rooms/` with no Verify, `Applies-to: ha/rooms/**` with a Verify, and `Applies-to: ha/rooms/` with a Verify, when `validate.py personas` runs, then it warns `persona-goal-scope` for the first (no check) and the second (naming `**` and the trailing-`/` form that replaces it), and not for the third.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::GoalScopeLintTests::test_validate_personas_warns_on_an_unchecked_or_misdialected_scope
- **AC3:** Given the End goal example `templates/personas/persona-template.md` carries in an `<!-- end-goal-example ... -->` comment under End Goals, when the test fills a fixture card's End Goals from it and runs `validate.py personas` and `sprint.py goal-review brief`, then the card draws no `persona-goal-*` warning, and a second card that keeps the comment unfilled lists only its own End goals in the brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::TemplateExampleTests::test_template_example_is_read_and_its_comment_is_not
- **AC4:** Given the `persona-goal-*` rule names `validate.py personas --format json` prints for the fixtures above, when the test reads the persona rule table in `reference-persona.md`, then every printed rule has a row naming it and the Applies-to dialect is stated beside it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::RuleTableTests::test_every_printed_persona_goal_rule_has_a_row

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the lint is never run, or reads every Verify line in the file, so the Scenario line is linted and the End goal's own line is missed
- AC2 must fail on: a scoped goal with no Verify passes, or a `**` pattern that matches one segment only passes silently, so the plan and the seed later say nothing about files the author meant to cover (LL0009)
- AC3 must fail on: the template documents a shape the reader does not parse (a Verify not nested under the numbered goal), or the reader takes the commented example as one of the card's End goals
- AC4 must fail on: a rule renamed or added in code with no row in the table RFC0061's persona review is to cite
- Serves: Maya Okafor #4 (specs, code and tests never quietly drift).
- One End goal reader in a new `scripts/lib/persona_goals.py` returning (number, text, verify, applies_to), skipping HTML comments and fenced code. `sprint.persona_cards` keeps `end_goals` as (number, text) pairs (sprint.py:11106 and two existing tests unpack them) and gains the Verify and Applies-to fields separately, read through the new reader; `sprint._end_goals` (sprint.py:9960) delegates to it.
- Applies-to dialect, named in the template and reference-persona.md: the TRD component rule (`sprint._component_names`, sprint.py:2677). Whole path segments, case-sensitive; a pattern ending `/` names every file beneath that directory, wherever the directory sits in the path (`ha/rooms/` matches `ha/rooms/up/bed.yaml` and `other/ha/rooms/x.yaml`, not `ha/rooms-old/x.yaml`); otherwise the path's trailing segments, with `*` inside one segment. `**` is not part of it (probe: `ha/rooms/**` misses `ha/rooms/up/bed.yaml`), so the lint warns on it rather than the matcher widening it, because the matcher is shared with the TRD constraints.
- Creates the reference-persona.md rule table (`persona-goal-verify`, `persona-goal-scope`); the Serves and seat-card stories add their rows, so RFC0061's persona review can cite rules by name.
- Regenerate reference-persona.md's reading guide (`docgen.py reading-guides`).
- RFC0061 workstream 1 ('testable goals' in the standard): D7 decides only whether this advisory ever blocks; a blocking mode would call this reader.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
