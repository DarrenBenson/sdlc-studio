# CR-0211: retros and reviews become first-class artifact types (tool-allocated ids and index rows)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Retros (RETRO) and reviews (RV) are the only recurring numbered artefacts still hand-authored end-to-end: the file is written by hand and its _index.md row is hand-edited, unlike every artifact.py type - inconsistent with the never-hand-author-an-index discipline the skill enforces for consuming projects. Observed twice in one day: RV0007's report id came from next_id but the file/index were manual; RETRO0017 was fully manual. Extend the artifact machinery (templates + SPEC entries + index templates) so 'artifact new --type retro/--type review' allocates the id, writes the scaffold and appends the index row; reconcile then covers their indexes for drift like every other type.

## Acceptance Criteria

- [ ] artifact.py new supports retro and review with tool-allocated ids, scaffold templates and index rows
- [ ] reconcile detect/apply cover retros/ and reviews/ indexes (count + row presence) without falsing on the existing hand-made history
- [ ] The sprint-close retro step and the review workflows reference the deterministic path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
