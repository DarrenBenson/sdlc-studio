# BG1736: The commit-msg attribution note advises a schema 3 id by its dashless key

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T04:11:09Z

## Summary

`engagement_floor.unnamed_unit_attribution` builds its note from the normalised key, so a commit staging a file that a schema 3 unit (BG-01JQK3F8) owns is told to add `Refs: BG01JQK3F8`, a spelling no artefact carries. BG1574 fixed the same defect in changelog.py's refusal; this is the second site. Found by BG1574's round-three qa review, pre-existing since 70b10324a.

## Steps to Reproduce

1. In a fixture project whose BG-01JQK3F8 record declares src/v3.py in its Affects, stage src/v3.py.
2. Commit with the message fix(BG9002): b.
3. Read the attribution note: it ends add `Refs: BG01JQK3F8`, not `Refs: BG-01JQK3F8`.

## Proposed Fix

Print each id in the note as its own artefact spells it, the way BG1574's repair does in changelog.py, and leave the sequential-id spelling unchanged.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `engagement_floor.unnamed_unit_attribution` builds its note from the normalised key, so a commit staging a file that a schema 3 unit (BG-01JQK3F8) owns is told...
- [ ] **AC2** The proposed fix lands, pinned by a test: Print each id in the note as its own artefact spells it, the way BG1574's repair does in changelog.py, and leave the sequential-id spelling unchanged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Filed |
