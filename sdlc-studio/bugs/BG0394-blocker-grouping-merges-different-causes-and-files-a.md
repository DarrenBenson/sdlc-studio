# BG0394: Blocker grouping merges different causes and files a CR naming one unit's remedy for many

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The group key is (stage, id-stripped remedy) but `cause` and the filed CR's summary come from `group['blockers'][0]`. Two blockers with different details and the same remedy merge, and the second detail never reaches the artefact - while the close prints that they 'are listed inside the artefact that covers them'. Separately, the CR's acceptance criterion names one unit's remedy while covering several, so it closes when one is done.

## Steps to Reproduce

`group_blockers([`{stage:gate,detail:'markdown lane red',remedy:'run the gate'},{stage:gate,detail:'neutrality guard red',remedy:'run the gate'}]) -> one group, cause 'markdown lane red' only.

## Proposed Fix

Key on the detail as well, list every member detail in the filed artefact, and template the criterion over group['units'].

## Acceptance Criteria

### AC1: two blockers with different details are not merged

- **Given** two blockers sharing a remedy and differing in what is actually wrong
- **When** it runs
- **Then** they stay two groups, so the second detail cannot vanish from the filed artefact while the close claims it is listed inside it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockerGroupingTests::test_two_blockers_with_different_details_are_not_merged
- **Verified:** yes (2026-07-29)

### AC2: blockers differing only in the unit still group

- **Given** one owed sign-off across several units
- **When** it runs
- **Then** they remain ONE group, because that is the property the grouping exists for and the fix must not cost it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockerGroupingTests::test_blockers_differing_only_in_the_unit_still_group
- **Verified:** yes (2026-07-29)

### AC3: a grouped artefact can list every blocker it covers

- **Given** a group of several blockers
- **When** it runs
- **Then** every member is kept on the group, so the artefact renders all of them and its criteria cover every unit rather than closing when one is done
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockerGroupingTests::test_every_member_is_kept_on_its_group
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
