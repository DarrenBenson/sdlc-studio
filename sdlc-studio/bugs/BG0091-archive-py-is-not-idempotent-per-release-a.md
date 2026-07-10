# BG0091: archive.py is not idempotent per release: a crash between its two writes duplicates every archived row invisibly

> **Status:** Fixed
> **Verification depth:** functional (red-then-green: crash-resume re-run does not duplicate archive rows; atomic writes; suite 1516)
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. archive.py appends moved rows to the archive file (step 1, a non-atomic full rewrite when it exists, :79-81) BEFORE trimming the live index (step 2, :102, also non-atomic), with no dedupe - the docstring claims 'Idempotent per release' (:11). Reproduced (RV0007): crash between steps then re-run -> the archive file holds each row twice; detect_duplicate_rows scans only the live _index.md (reconcile.py:270-274) so the duplication is permanently unflagged. Policy divergence from the consolidated walker: reconcile.archive_plan excludes already-archived ids (:1279-1288) and refuses loudly on unrecognised statuses (:1261-1269) while archive.py:63 silently skips them (CR0182 consolidated the walker, not the policy or write order).

## Steps to Reproduce

Archive a release; simulate a crash after the archive-file write but before the live-index trim; re-run archive -> duplicate rows in archive/<release>/<type>.md; reconcile detect stays quiet.

## Proposed Fix

Dedupe appends against ids already in the archive file (mirror archive_plan); write both files via atomic_write; extend detect_duplicate_rows to archive sub-indexes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
