# BG0099: artifact new/batch cannot link a story to a v3 ULID epic: `_find_epic` splits the id on the first dash

> **Status:** Fixed
> **Verification depth:** functional (red-then-green: story links to a v3 ULID epic; e2e greenfield story on schema-3 epic_linked=True; suite 1523)
> **Severity:** High
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Found dogfooding the EP0026 close eval (greenfield create on a schema-v3 project). artifact.`_find_epic` (scripts/artifact.py:184) resolves the parent epic with sdlc_md.norm_id(`p.stem.split('-')[0]`); for a v3 ULID filename EP-01KX4XE7-reading.md that split yields 'EP', which matches no epic, so 'artifact new --type story --epic EP-01KX4XE7' fails 'epic ... not found - create it first' and the story is not wired into the Story Breakdown. Reproduced end-to-end. This BLOCKS the flagship greenfield story-generation flow on v4's DEFAULT schema (init seeds schema_version: 3): a fresh v4 project cannot create a story under its epic via the deterministic tool. `extract_record_id(stem)` returns the correct full id (verified: 'EP-01KX4XE7' vs the split's 'EP'); the same class as BG0072 (all-alpha/naive id parse vs ULID). `_wire_story_to_epic` (:187) and batch (:439) route through the same `_find_epic`, so both new and batch are affected.

## Steps to Reproduce

schema_version: 3 workspace; artifact.py new --type epic --title x (mints EP-<ulid>); artifact.py new --type story --epic EP-<ulid> --title y -> error: epic EP-<ulid> not found. Confirm: sdlc_md.extract_record_id('EP-<ulid>-x') returns the full id, `p.stem.split('-')[0]` returns 'EP'.

## Proposed Fix

In `_find_epic`, resolve via sdlc_md.extract_record_id(p.stem) (era-aware, used elsewhere) instead of `p.stem.split('-')[0]`; a v2 stem (EP0001-x) and a v3 stem (EP-01.. -x) both yield the correct id. Add a v3 fixture test for the story->epic wiring.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
