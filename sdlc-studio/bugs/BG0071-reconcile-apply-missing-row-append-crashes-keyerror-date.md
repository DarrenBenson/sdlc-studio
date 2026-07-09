# BG0071: reconcile apply missing-row append crashes KeyError 'date' on any index with a date column

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: BLOCKS v4.0 tag. row_from_header (lib/sdlc_md.py:231-232) indexes f['date'] directly for created/date/raised/updated header cells while every other column uses f.get(); reconcile's missing-row append (reconcile.py:943) passes an empty dict. The shipped cr/bug/plan index templates all carry a Date/Created column, as do all of this repo's own indexes, so the advertised self-heal path crashes (exit 1, --dry-run included) whenever a file lacks an index row. Cascades: transition set --ids aborts mid-batch AFTER stamping the artefact file (file transitioned, index unsynced - the crashed-writer state the healer exists to fix); migrate_v3 step 3 and project_upgrade --with-reconcile route through the same call. Reproduced independently by two review legs (RV0007).

## Steps to Reproduce

Workspace from the shipped bug index template; delete one row from bugs/_index.md; run reconcile.py apply --scope bugs -> error: 'date', exit 1. Or transition.py set --ids over a missing-row artefact: file stamped, batch aborts.

## Proposed Fix

sdlc_md.py:232 -> out.append(f.get('date', '--')); add a seam test appending a missing row into a dated index.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
