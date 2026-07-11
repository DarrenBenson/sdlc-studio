# BG0109: file_finding.py hardcodes 'audit' as the revision-history author, ignoring --author

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

`file_finding.py` writes '| {today} | audit | Filed |' (three hardcoded sites, ~L117/129/139) into Revision History regardless of the --author flag, which is only used in the body context. RFC0029 was filed today with --author 'Claude (Fable 5)' and its history row says 'audit'. Cosmetic until someone audits authorship - then it is a wrong provenance record produced by the provenance tooling.

## Steps to Reproduce

1. `file_finding.py` file --type rfc --title X --author 'Someone'. 2. Open the artefact's Revision History: author column reads 'audit'.

## Proposed Fix

Use args.author (fallback 'audit') in the revision-history rows.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
