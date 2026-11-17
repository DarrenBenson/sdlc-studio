# US1302: The sprint report counts the high-risk units reviewed by a different model family, out of how many

> **Status:** Draft
> **Depends on:** US1301
> **Risk-class:** standard
> **Delivers:** CR0732
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cross_family.py, changelog.d/US1302.md
> **Epic:** EP0369
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report counts the high-risk units reviewed by a different model family, out of how many
**So that** CR0732 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report counts high-risk units reviewed by another family

- **Given** a closed run whose batch holds three high-risk units: one reviewed by a different family, one by the same family, one with a model recorded as unknown
- **When** the sprint report is built
- **Then** it states that 1 of 3 high-risk units was reviewed by a different model family, and names the same-family unit and the unknown unit separately; only each unit's latest delivery verdict is counted. Fails on: an unknown family counted as different, or a unit counted once per review round
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cross_family.py::CrossFamilyLineTests::test_the_report_counts_cross_family_reviews_of_high_risk_units

### AC2: No high-risk unit, no figure

- **Given** a closed run with no high-risk unit
- **When** the sprint report is built
- **Then** no cross-family figure is printed. Fails on: a `0 of 0` line read as a measured result
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cross_family.py::CrossFamilyLineTests::test_a_run_with_no_high_risk_unit_prints_no_figure

## Notes

- Read the family through `lib/model_family.py` (US1300), never a second table.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
