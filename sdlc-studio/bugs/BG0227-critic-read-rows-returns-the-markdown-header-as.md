# BG0227: critic._read_rows returns the markdown header as a data row for any table whose first column is not Unit

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The header-skip at critic.py:190 is hardcoded to cells[0] in ('Unit',). The evidence and sign-off tables begin with a Unit column so their headers are skipped; the sprint-review table begins with Base, so `record_sprint_review`'s header row has been returned as data since that table was added. Currently LATENT: both production callers filter rows by unit id and the header's Units cell never normalises to a real id, so no shipped behaviour is wrong today. It goes live the moment anything counts, sums or iterates the rows without an id filter - which is what the per-round cost accumulation in US0264 does.

## Steps to Reproduce

In a temp repo call `critic.record_sprint_review(root`, ['US0001'], reviewer='seat', author='builder', verdict='approve', findings='f') once, then len(`critic.sprint_reviews(root)).` Observed: 2. Expected: 1. The extra row is {'base': 'Base', 'reviewer': 'Reviewer', ...} - the markdown header parsed as data.

## Proposed Fix

Skip a row whose cells equal the declared column names (compare case-insensitively against cols), rather than hardcoding one table's first-column literal. That generalises to every table `_read_rows` serves and cannot silently lapse when a new table with a different first column is added.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
