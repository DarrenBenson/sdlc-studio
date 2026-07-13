# BG0117: a prose field can invent a metadata line in an artefact body; the low-consolidation bullet squeezes a summary onto one line

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering BG0115 (2026-07-13), and deliberately NOT fixed there. BG0115 refuses a line break in every field that lands in a metadata line or a table cell. Prose fields (summary, steps, fix, impact, recommendation) are correctly left unguarded, because multi-line IS the point of a section body. Two residuals follow. First, a prose field can introduce a '> **Field:**' line into the artefact BODY. This is harmless for a field already present in the head (`extract_field` takes the first match, so the head wins), but it can invent a field the head lacks, and a reader - human or script - may take it for provenance. Second, `triage_noise._bullet` squeezes a summary into a one-line bullet on the low-severity consolidation path, so a multi-line summary is silently flattened. Neither can forge provenance in the head nor execute anything, so neither is a security defect. Refusing prose would break legitimate filings: this needs a RENDERING fix, not a refusal.

## Steps to Reproduce

1. `file_finding.py` file --type bug --title t --summary $'ok\n> **Waived:** yes'. 2. The artefact body carries a '> **Waived:**' line the head never declared. 3. Separately: file a Low-severity finding on schema v3 with a multi-line summary and read the consolidation CR's bullet - the summary is flattened onto one line.

## Proposed Fix

Render prose fields so a line that looks like a metadata declaration cannot be mistaken for one - indent or fence the body, or escape a leading '> **' in prose. Fix _bullet to render a multi-line summary faithfully rather than squeezing it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
