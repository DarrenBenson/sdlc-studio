# US1322: A project upgrading to the persona standard is set to report mode, so its own cards are named, not refused, until it switches the standard on

> **Status:** Draft
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_standard_mode.py, changelog.d/US1322.md, .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0287
> **Points:** 3
> **Persona:** Jonah Reyes
> **Depends on:** US1055

## User Story

**As a** team lead upgrading an inherited repository to a release that holds persona cards to a standard
**I want** the upgrade to name my own cards that break the standard without refusing them, until I switch the standard on
**So that** an upgrade never stops a review, a refine or a triage mid-sprint, and I turn the gate on when my cards are ready

## Acceptance Criteria

- **AC1:** Given `personas.standard: report` in a project's config and a project qa seat card carrying a demographic token, when `persona_resolve.py resolve --seat qa --render review` and `critic.py brief --unit US0001 --seat qa` run, then each frames the card and exits 0, printing one stderr line that starts `persona card blocked (report mode):` and names the card, the rule and the remedy command; with the key set to `block`, or absent, both refuse as US1055 AC1 says. Fails on: report mode printing no line, or block mode framing the card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard_mode.py::PersonaStandardModeTests::test_report_mode_names_a_blocked_card_and_frames_it
- **AC2:** Given a project whose config has no `personas.standard` key and that holds its own seat or persona cards, and a second project holding none, when `project_upgrade.py` upgrades each to this release, then the first gains `personas.standard: report` in its config and the upgrade reports that change with the one setting that switches the standard on, and the second's config is unchanged. Fails on: the upgrade leaving the first without the key, or writing it for the second.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard_mode.py::PersonaStandardModeTests::test_an_upgrade_sets_report_mode_only_for_a_project_with_its_own_cards
- **AC3:** Given `templates/config-defaults.yaml` and `reference-config.md`, when they are read, then each documents `personas.standard` with the values `block` and `report`, its default `block`, and the upgrade's `report` setting; and given an unknown value such as `warn`, when `persona_resolve.py resolve --seat qa` runs on the token-carrying card, then it refuses as under `block` and prints one stderr line naming the key and its two values. Fails on: an unknown value read as report, or the key undocumented in either file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard_mode.py::PersonaStandardModeTests::test_the_key_is_documented_and_an_unknown_value_fails_safe

## Notes

- D0374 consult, 2026-11-20 (D0553): Jonah Reyes objected that US1055's refusal arrives on the day an inherited repository upgrades, with no step to adopt it. New projects get `block`, the PRD's default for a gate-bearing key; an upgrading project with its own cards gets `report`, a change the upgrade makes and reports rather than a gate it springs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Created via `new` (deterministic) |
