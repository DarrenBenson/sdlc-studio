# US1301: `review.cross_family` (off by default, warn, block) decides whether a same-family verdict counts as a high-risk unit's independent review

> **Status:** Draft
> **Depends on:** US1300
> **Risk-class:** high
> **Delivers:** CR0732
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family_gate.py, changelog.d/US1301.md
> **Epic:** EP0369
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `review.cross_family` (off by default, warn, block) decides whether a same-family verdict counts as a high-risk unit's independent review
**So that** CR0732 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Off by default changes nothing (D0515)

- **Given** a project with no `review.cross_family` key and a unit whose Risk-class is high
- **When** an APPROVE is recorded with both models in the anthropic family
- **Then** it counts as the unit's independent review, nothing about families is printed, and `templates/config-defaults.yaml` and `reference-config.md` both state `off` as the default. Fails on: a default of warn or block, or a family warning printed under off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family_gate.py::DefaultTests::test_off_by_default_counts_a_same_family_review_silently

### AC2: Block stops a same-family or unknown-family review clearing a high-risk unit, and only a high-risk one

- **Given** `review.cross_family: block`
- **When** a same-family APPROVE is recorded on a high-risk unit, an APPROVE with one model `unknown` on another high-risk unit, and a same-family APPROVE on a standard unit
- **Then** both high-risk verdicts are written but `independence` reads neither as the unit's independent review, each naming the two models (or the unknown side) and the setting; the standard unit's verdict counts. Fails on: a same-family or unknown-family review clearing a high-risk unit, or block reaching a unit of class standard or elevated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family_gate.py::BlockTests::test_block_refuses_same_and_unknown_family_on_high_risk_units_only

### AC3: Warn counts and says so; a high-risk record with no models is refused under warn or block

- **Given** `review.cross_family: warn`
- **When** a same-family APPROVE is recorded on a high-risk unit, then a record on a high-risk unit names neither model, then the key is set to `strict`
- **Then** the first counts, prints one warning naming both models and is marked so a report can count it; the second is refused with nothing written, naming `--author-model` and `--reviewer-model`; `strict` is refused naming off, warn and block. Fails on: a high-risk record with no models written under warn, or an unknown value read as off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family_gate.py::WarnTests::test_warn_counts_and_a_record_without_models_is_refused

## Notes

- `scripts/tests/test_lean_config_keys_read.py` (BG0831) holds every documented key to a reader: the key must be read by `critic.py`, not only documented.
- Risk class comes from the story's `Risk-class` field (`lib/risk_class.py`); a bug's class derives from its Affects the same way the plan does.
- This repo declares no component map, so every unit here is standard and the setting does nothing in this repository until one is declared.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
