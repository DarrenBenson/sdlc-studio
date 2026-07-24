# BG0291: refine's seeded ACs duplicate their own label and restate the story title as the Then clause

> **Status:** Fixed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Verification depth:** functional (label de-duplication, placeholder Then, and full transcription of a truncated criterion; 3 of 5 tests red before the change, the other 2 declared as characterisation in their docstrings)
> **Severity:** Medium
> **Points:** 2

## Summary

A seeded AC block repeats its own `ACn:` label in the heading and restates that heading as
the `Then`, so the criterion asserts nothing observable while reading as authored work.

## Steps to Reproduce

Refine a request whose criteria are written to the story template, so each already opens
with its own label:

```bash
# CR0001 carries `- [ ] AC1: plan-time overlap detection that does not depend on verifiers`
refine.py apply --request CR0001 --into EP0156 --story "Overlap detection|3"
# story:  ### AC1: AC1: plan-time overlap detection that does not depend on verifiers
#         - **Then** AC1: plan-time overlap detection that does not depend on verifiers
```

## Proposed Fix

Strip a leading `ACn:` label from the criterion before the seed prepends its own, and leave
the `Then` an explicit placeholder: the criterion is the heading, and a Then that restates
the heading is the vacuous criterion the verify DSL exists to refuse. Where the heading has
to truncate a long criterion, transcribe the full text under the block so nothing is lost.

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
- **Verified:** yes (2026-07-24)

### AC2: a seeded Then is not the heading restated

- **Given** the same seed
- **When** the story is written
- **Then** the `Then` clause is either a placeholder or an outcome, never a copy of the heading - a criterion that states its own title asserts nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededAcShapeTests::test_the_then_clause_is_not_the_heading
- **Verified:** yes (2026-07-24)

### AC3: a story is not seeded with a sibling's criterion

- **Given** a request with 3 ACs decomposed into 2 stories
- **When** refine seeds
- **Then** no story receives a criterion that belongs to a different story's slice; where the mapping is not determinable the marker is used instead of a guess
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededAcShapeTests::test_no_story_gets_a_siblings_criterion
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Fixed: `_strip_ac_label` removes a criterion's own label before the seed adds one, the `Then` is now `{{observable outcome}}`, and a truncated criterion is transcribed in full under its block. AC3 (no sibling's criterion) was already held by the multi-story guard and is now pinned. `SeededAcShapeTests` in `test_refine.py`. |
