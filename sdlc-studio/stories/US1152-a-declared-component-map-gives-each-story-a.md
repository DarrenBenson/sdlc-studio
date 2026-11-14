# US1152: A declared component map gives each story a risk and compliance class at refine

> **Status:** Ready
> **Delivers:** CR0696
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/risk_class.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_refine_add_into.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py, changelog.d/US1152.md
> **Epic:** EP0307
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** a declared component map gives each story a risk and compliance class at refine
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given a project whose committed config declares a component map (path prefixes to a class: standard, elevated or high), when `refine apply` mints a story, then the story carries a Risk-class field equal to the highest class among the components its Affects touch.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::RefineStampsClassTests::test_story_takes_highest_class_of_its_affects
- **AC2:** Given no component map, when `refine apply` runs, then every story is standard, one line says no map is declared, and the command exits 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::NoMapTests::test_no_map_means_standard_one_line_exit_zero
- **AC3:** Given a map entry naming an unknown class, when `refine apply` runs, then it reports the entry in one line, treats it as standard, and still mints the stories.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::BadMapTests::test_unknown_class_is_reported_not_refused

## Notes

- Serves Abena Osei's End goal 1; delivers part of CR0696 (D0476).
- AC1 must fail on: First-match instead of highest-class; the field written when Affects is empty; a story touching only unmapped paths not defaulting to standard.
- AC2 must fail on: A refusal or non-zero exit without a map; two or more lines; a story left with no class field.
- AC3 must fail on: An exception or refusal on a bad entry; the bad entry silently dropped with no message; the unknown class written onto a story.
- D0439's machinery tag is NOT implemented in code (decisions.md D0439/D0444/D0445 say the orchestrator tags by hand until RFC0063 WS7), so there is no existing tag or path-map code to copy. The nearest code pattern is the TSD risk-area path matcher: scripts/sprint.py:13170 `test_strategy` (matches each unit's Affects against level paths) and `render_test_strategy` :13209.
- Put the map reader and classifier in a new `scripts/lib/risk_class.py`: `load_map(root`), classify(files) returning (class, components), rank order standard < elevated < high. Declare in sdlc-studio/.config.yaml under risk.components, read via `sdlc_md.project_override` `(lib/sdlc_md.py:1812`); add the default (empty) to templates/config-defaults.yaml and document in reference-config.md. Decide and note the exact config shape in the story; keep the vocabulary to the three classes so ordering is defined.
- refine writes story fields where it sets fields['affects']: scripts/refine.py:281-284 and :375-378 (two paths: apply and add); Affects resolution at :604 `resolve_story_affects`. Set the class after Affects resolves, including 'inherited' and 'seeded' modes. Story template scripts/../templates/core/story.md:19 shows the Affects header to mirror. Check artifact.py new accepts an arbitrary field before choosing the field name.
- Bugs do not pass through refine; the plan story derives a class for a unit with no stored tag from its Affects.
- Template and help text are consuming-facing: British English, no em dashes, no internal ids.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
