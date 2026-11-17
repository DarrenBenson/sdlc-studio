# US1246: The rendered lane brief and review brief take the accepted cuts, with every gated rule's text still present

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0700
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py, changelog.d/US1246.md
> **Epic:** EP0342
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The rendered lane brief and review brief take the accepted cuts, with every gated rule's text still present
**So that** CR0700 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The rendered lane brief is smaller and still names every gated rule

- **Given** the module's fixture project and the size its lane brief rendered to before the cuts, held as a constant
- **When** `sprint.py lane brief --units <id>` renders the brief
- **Then** the brief is smaller than the constant, and still carries the criteria as the contract, the Affects as the only files staged, the hand-in files, the call budget with its hand-off note, and the instruction to leave the commit to `sprint lane land`. Fails on: a cut that removes the text of a rule `lane land`, the staging check or the self-check gate enforces
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::RenderedBriefCutsTests::test_the_lane_brief_is_smaller_and_keeps_every_gated_rule

### AC2: The rendered review brief is smaller and still carries its law

- **Given** the same fixture and the size its review brief rendered to before the cuts
- **When** `critic.py brief --unit <id> --seat qa` renders the brief
- **Then** the brief is smaller than the constant, and still carries the seat charter, the unit's Affects as scope, the criteria, the claim-inventory pass, the verdict file path and the record command. Fails on: a review brief that drops any part `critic.py record` or the verdict contract depends on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::RenderedBriefCutsTests::test_the_review_brief_is_smaller_and_keeps_its_law

### AC3: Every accepted cut to the rendered text is made

- **Given** CR0700's audit rows citing `sprint.py` or `critic.py`
- **When** both briefs are rendered
- **Then** the quoted text of every `changed` or `removed` row appears in neither brief, and the quoted text of every `kept` row still appears in the brief it was audited in. Fails on: an accepted cut left in the rendered text, or a kept rule cut
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::RenderedBriefCutsTests::test_accepted_cuts_are_gone_from_the_rendered_briefs

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
