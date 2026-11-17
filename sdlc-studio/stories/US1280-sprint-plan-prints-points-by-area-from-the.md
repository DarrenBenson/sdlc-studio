# US1280: Sprint plan prints points by area from the tags and from a path map, naming any unit whose tag disagrees

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0722
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_machinery_share.py, sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md
> **Epic:** EP0360
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint plan prints points by area from the tags and from a path map, naming any unit whose tag disagrees
**So that** CR0722 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The plan prints points by area from the tags

- **Given** a batch whose units each carry an `Area` field (product, cost, evidence or machinery, D0439), `Points` and an `Affects` list
- **When** `sprint.py plan` runs over the batch
- **Then** it prints the batch's points for each area as read from the tags, with the machinery share as a fraction of the batch's points, and a unit with no `Area` field is counted under its own untagged line and named, never folded into an area. Fails on: a plan that prints no share, or one that counts an untagged unit as product and so understates machinery
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_machinery_share.py::MachineryShareTests::test_the_plan_prints_points_by_area_from_the_tags

### AC2: The plan prints points by area a second time, from the path map

- **Given** the same batch, and the path map shipped in `templates/config-defaults.yaml` that marks the loop scripts, `tools/`, `.githooks/` and `.github/` as machinery
- **When** `sprint.py plan` runs over the batch
- **Then** it prints a second share computed from each unit's `Affects` against the path map, beside the first and labelled apart from it, and a project that overrides the map in its own configuration gets the share by its own map. Fails on: one share printed under both labels, or a path map fixed in code that a project cannot change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_machinery_share.py::MachineryShareTests::test_the_plan_prints_a_second_share_from_the_path_map

### AC3: A unit whose tag disagrees with its files is named

- **Given** a batch holding one unit tagged cost whose `Affects` lies wholly in machinery paths, and one unit tagged machinery whose `Affects` does too
- **When** `sprint.py plan` runs over the batch
- **Then** the plan names the first unit as tagged cost but touching machinery paths, does not name the second, and exits as it would without the share lines. Fails on: a disagreement left unreported, a unit in agreement flagged, or the flag turned into a refusal, which D0439 rules out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_machinery_share.py::MachineryShareTests::test_a_unit_whose_tag_disagrees_with_its_affects_is_named

### AC4: RFC0063 names the request that tools WS7

- **Given** `sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md`
- **When** its `Decomposed-into` line and the WS7 row of its Phased Plan are read
- **Then** both name CR0722, and `reference-sprint.md` describes the two share lines and the disagreement flag where it describes the plan's output. Fails on: the WS7 row still reading 'CR (new)' with no id, which leaves the deferral tracked by nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
