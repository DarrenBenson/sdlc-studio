# BG0115: authorship_value accepts a multi-line author, corrupting the Raised-by line and the index row

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0109 review (2026-07-13) while attacking the new shared revision-row writer, and PROVED to reproduce at baseline commit 4cd3067 with BG0109's diff reverted - so it is BG0108's surface (the authorship resolver), not BG0109's. `sdlc_md.authorship_value()` accepts an author containing a newline and passes it through. `join_row` escapes a pipe but not a newline, so the value breaks out of its table cell and out of its metadata line. Baseline reproduction with --author 'Sam\nEvil: injected': the metadata renders as '> **Raised-by:** Sam' followed by a bare line 'Evil: injected; human;', and the index row splits across two lines. A creator can therefore be made to write arbitrary lines into an artefact's metadata block through the author field - the provenance tooling forging provenance.

## Steps to Reproduce

1. artifact.py new --type bug --title t --author $'Sam\nEvil: injected'. 2. Open the artefact: the Raised-by metadata line is broken across two lines and the index row is corrupted. Reproduces at commit 4cd3067 without BG0109's changes.

## Proposed Fix

Refuse a multi-line author in `sdlc_md.authorship_value()`, exactly as `artifact._verifiers_of` already refuses a multi-line Verify expression. Fail loud at the resolver, so every creator inherits the refusal rather than each escaping separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Sam Eriksson | Filed |
