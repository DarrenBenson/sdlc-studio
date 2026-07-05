# CR-0162: artifact revision verb: deterministic batch appends to Revision History

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

Sprint-close revision-history rows were hand-scripted with an ad-hoc python loop this sprint - a mechanical task without a tool verb. artifact.py gains revision --ids A,B --note ... [--author ...]: one dated row appended per artifact, loud refusal when a Revision History section is missing, slug-anchored file lookup.

## Acceptance Criteria

- [ ] revision appends exactly one dated row per id in a batch; the table's structure is preserved
- [ ] a file without a Revision History section is refused loudly, not silently skipped; exit non-zero if any id refused
- [ ] regression tests anchor on slugs, never display ids

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
