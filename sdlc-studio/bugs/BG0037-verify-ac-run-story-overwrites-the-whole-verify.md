# BG0037: verify_ac run --story overwrites the whole verify-report.json instead of merging, breaking the Done-gate for batch sprints

> **Status:** Fixed
> **Severity:** high
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

write_report builds verify-report.json from ONLY the stories in the current run and write_text-overwrites it (scripts/verify_ac.py). So verifying a sprint one story at a time leaves the report holding ONLY the last story - and transition->Done (CR0084) reads that report, so the gate fails 'no verify result' for every earlier story. A field agent delivering 11 stories hit exactly this: per-story verify then transition US0011->Done failed because the report had been clobbered. The only workaround is --dir, which re-stamps EVERY story in the directory (re-running verifiers on already-Done foundation stories, e.g. US0002-US0004 showing 0/7) - alarming and wasteful.

## Steps to Reproduce

1. verify_ac run --story US0011 (report holds US0011). 2. verify_ac run --story US0012 (report now holds ONLY US0012). 3. transition set --id US0011 --status Done -> blocked: the report has no US0011 entry. Workaround --dir re-verifies the whole directory, re-stamping unrelated Done stories.

## Proposed Fix

Make write_report MERGE: load the existing verify-report.json stories dict, update only the entries for stories in this run, preserve the rest, then write. Per-story verification then accumulates; the Done-gate finds every verified story; --dir is no longer required just to populate a multi-story report. Add --fresh to force a clean rebuild; dry-run keeps writing to the distinct .dry-run path. Unit test: two sequential single-story runs leave BOTH stories in the report; --fresh overwrites.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Filed |
