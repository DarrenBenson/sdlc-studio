# BG0291: refine's seeded ACs duplicate their own label and restate the story title as the Then clause

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Severity:** Medium
> **Points:** 2

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit planning RUN-01KYA8CF. `refine apply --into EP0156` seeded ACs onto US0415-US0418 that
restate their own label and their own title:

```markdown
### AC1: AC1: plan-time overlap detection that does not depend on verifiers

- **Given** {{context}}
- **When** {{action}}
- **Then** AC1: plan-time overlap detection that does not depend on verifiers
- **Verify:** {{executable check}}
```

Three defects in four lines. The heading carries `AC1:` twice, because the seed prepends the
label to a source string that already begins with it. The `Then` clause is the heading again,
so the criterion states its own name instead of an observable outcome - and a `Then` that
restates the title is exactly the vacuous criterion the verify DSL exists to refuse. And the
seeded text is drawn from the REQUEST's ACs regardless of which story it lands on, so a story
gets a criterion belonging to a sibling.

This is worse than the ungroomed marker it replaces: the marker is honestly empty and reads as
work owed, while this looks authored. A groomer skimming the file sees filled-in criteria.

## Impact

Every `refine apply` that seeds ACs, which is the default. The output passes `validate`, so
nothing downstream catches it - it is caught only by a human reading the story.

## Acceptance Criteria

### AC1: a seeded heading carries its label once

- **Given** a request AC whose text already begins with `ACn:`
- **When** refine seeds it onto a story
- **Then** the heading reads `### AC1: <text>` with the label appearing exactly once
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededAcShapeTests::test_the_label_is_not_doubled

### AC2: a seeded Then is not the heading restated

- **Given** the same seed
- **When** the story is written
- **Then** the `Then` clause is either a placeholder or an outcome, never a copy of the heading - a criterion that states its own title asserts nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededAcShapeTests::test_the_then_clause_is_not_the_heading

### AC3: a story is not seeded with a sibling's criterion

- **Given** a request with 3 ACs decomposed into 2 stories
- **When** refine seeds
- **Then** no story receives a criterion that belongs to a different story's slice; where the mapping is not determinable the marker is used instead of a guess
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededAcShapeTests::test_no_story_gets_a_siblings_criterion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
