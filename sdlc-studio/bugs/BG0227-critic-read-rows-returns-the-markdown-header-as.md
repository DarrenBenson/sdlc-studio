# BG0227: critic._read_rows returns the markdown header as a data row for any table whose first column is not Unit

> **Status:** Fixed
> **Verification depth:** functional
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

## Resolution

The code fix was ALREADY at HEAD when this was picked up: commit 0798ece (US0261/US0262,
2026-07-20 18:14) replaced `cells[0] in ("Unit",)` with a whole-tuple match against the
declared `cols`, exactly as the Proposed Fix asks. No production change was needed and none
was made. What was missing was the pin - the property survived only incidentally, through a
length assertion inside `test_verdict_without_an_open_run_reports_rather_than_counts`, a test
about run-state attribution.

Confirmed the defect first by reverting `_read_rows` to its pre-0798ece form: one recorded
sprint review then read back as two rows, the extra one being
`{'base': 'Base', 'reviewer': 'Reviewer', ...}`, the header parsed as data - the filed
reproduction, observed verbatim.

Added `ReadRowsHeaderTests` in `scripts/tests/test_critic.py`, three cases:

- the sprint-review table (led by `Base`) reads back exactly its one data row;
- a table whose columns share no name with any shipped table still loses its header, reaching
  `_read_rows` directly - this is what makes the docstring's "cannot lapse when the next one is
  added" claim earned rather than asserted;
- a data row whose FIRST cell alone reads `Unit` is kept, because only the whole row matching
  the column names is a header.

Mutation-proven (bytecode purged, `python3 -B`): reverting to the first-column literal kills the
first two plus the incidental pin; deleting the header skip entirely kills all three; a
first-column-NAME match (the near-miss fix) kills the third alone.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Fixed - code already at HEAD, behaviour pinned by three mutation-proven tests |
