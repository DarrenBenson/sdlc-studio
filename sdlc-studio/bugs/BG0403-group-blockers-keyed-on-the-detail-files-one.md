# BG0403: group_blockers keyed on the detail files one CR per unit again, and cannot see a v3 id at all

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent review of RUN-01KYNKDP: three done-gate blockers produce three groups; three identical sign-off blockers on ULID units produce three groups with `units: []` on each.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0394 added the detail to the group key so two blockers with different causes stop merging. It also destroyed the property the grouping exists for, in two ways.

1. `_done_gate_preflight` builds `detail = f'{unit}: {exception first line}'`, and the exception names the unit's own failing criterion. Three units failing the done gate now produce three groups and `--file-and-close` files three change requests for one owed action - the exact fan-out CR0495 was raised to stop.

2. `_UNIT_IN_DETAIL` is `\b((?:US|BG|CR|EP|RFC)-?\d{3,})\b`, which cannot match `US-01JQK3F8`. On a schema-v3 project the id is not masked out of the detail, so three identical sign-off blockers produce three groups, each with `units: []` - and the per-unit acceptance criteria the same change added are therefore empty, so the artefact names none of the units it covers. Under the old `(stage, remedy)` key these grouped correctly on any id scheme.

## Steps to Reproduce

1. `group_blockers` over three done-gate blockers whose details name their own units and criteria -> 3 groups.
2. `group_blockers` over three sign-off blockers on `US-01JQK3F8`-style ids -> 3 groups, `units: []`.

## Proposed Fix

Mask the unit out of the detail with the SAME id grammar the rest of the tree uses (`sdlc_md.ID_SEARCH_RE`, which reads both eras) before keying, so a v3 id is masked exactly as a v2 one is. Then key on the masked detail: two blockers differing only in which unit they name still group, and two with genuinely different causes still do not.

## Acceptance Criteria

- [ ] Three blockers differing only in the unit they name remain ONE group, on both id eras.
- [ ] Two blockers with genuinely different causes remain two groups.
- [ ] A grouped artefact names every unit it covers, including v3 ULID units.
- [ ] The id masking uses the shared grammar rather than a local pattern, so a third era is covered on the day it is declared.

## Impact

One owed sign-off arriving as N identical change requests is the cost CR0495 measured and removed; this reintroduces it for done-gate blockers and for every schema-v3 project. A grouped artefact that names none of the units it covers cannot be closed against them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
