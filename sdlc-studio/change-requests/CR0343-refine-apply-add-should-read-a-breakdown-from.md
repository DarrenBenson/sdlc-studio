# CR-0343: refine apply/add should read a breakdown from a file, not only repeated --story CLI args

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Refining a large backlog means hand-constructing many --story 'title|points|affects' CLI args per request (RUN-01KXQH64: ~56 stories across 12 refine calls, each a long shell line). It is verbose and error-prone (a typo in a points value or a stray pipe fails the whole call), and there is no way to review the whole breakdown as data before minting. A --breakdown <file.json/yaml> input (request -> epic-title/into + stories) would make bulk refine reviewable and re-runnable.

## Impact

Bulk refine (decompose a whole triaged backlog) is done via long fragile shell lines; a mistake is caught only at mint time, and the breakdown cannot be reviewed or version-controlled as a unit before it is applied.

## Acceptance Criteria

- [ ] refine apply and refine add accept --breakdown <file> (JSON or YAML) describing the epic title (or --into target) and the stories (title, points, affects); it validates the whole file before minting anything (the existing fail-empty discipline) and is equivalent to the repeated --story form.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
