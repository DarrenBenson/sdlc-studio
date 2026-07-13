# BG0117: a prose field can invent a metadata line in an artefact body; the low-consolidation bullet squeezes a summary onto one line

> **Status:** Fixed
> **Verification depth:** functional
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

## Delivered

Core fix delivered: `file_finding._prose_safe` escapes the bold delimiters of any prose `**Field:** value` declaration at either place `extract_field` anchors a field - a line start (optional blockquote `>`) OR an inline ` · `-separated run - so a summary/steps/fix/impact/recommendation body can no longer forge a metadata declaration `extract_field` (or a reader) reads as provenance. The escape mirrors `extract_field`'s anchor tokens AND its whitespace class exactly (`[^\S\n]` = all of `\s` bar newline), so it fires at a position iff `extract_field` would read a field there: no wider (a `**bold:**` mid-sentence, anchored to neither, renders untouched) and no narrower (an invisible NBSP or thin space after the anchor is caught). A `·\n**Field:**` run is caught by the line-start branch, since the field then opens a line; the `·` branch stays horizontal-only so it never swallows a newline in a multiline body. Wired into both create paths (`file_finding._render` and `artifact.py`'s `_text` / `_rendered` / `_fill_impact`). Test-first, mutation-checked, with a property check confirming equivalence to `extract_field` across the whole non-ASCII whitespace class. The author's words are kept verbatim (nothing dropped); the line renders as literal `**Field:**` text.

(Repaired across three independent-critic rounds: the first pass mirrored only the line-start branch; the second added the inline `·` branch; the third widened the post-anchor whitespace from `[ \t]` to `[^\S\n]` so non-ASCII whitespace - NBSP and friends - no longer leaks. The lesson: when mirroring another regex, mirror its character classes too, not just its anchor tokens, and prove it across the whole class rather than a sample of ASCII inputs.)

The secondary `triage_noise._bullet` flattening is left to CR0238, which owns `triage_noise.py` in this wave (avoids a two-agent edit of `_bullet`). This bug stays Open until that part lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
| 2026-07-13 | Dani Okafor | Prose-body metadata-line escape delivered (test-first, mutation-checked); `_bullet` flattening deferred to CR0238 |
