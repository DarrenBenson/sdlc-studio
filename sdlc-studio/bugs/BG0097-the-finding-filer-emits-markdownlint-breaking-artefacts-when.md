# BG0097: the finding filer emits markdownlint-breaking artefacts when prose contains underscore identifiers

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Dogfooded during RV0007: file_finding/artifact render summaries, steps and fix text verbatim, so prose containing snake_case or dunder identifiers (`_next_number`, `__main__`, `('-', 1)[1]`) produces artefacts that fail the repo's own markdownlint gate (MD037 spaces-inside-emphasis, MD050 strong-style, MD011 reversed-link). Six of RV0007's 33 filed artefacts needed hand post-editing to pass lint - the tool that refuses hollow artefacts should not mint lint-red ones.

## Self-demonstration

This very artefact reproduced the defect at filing time: its rendered summary/steps failed markdownlint (MD011/MD037/MD050) until hand-edited - the identifiers below are now backticked by hand, which is exactly the fix the tool should apply.

## Steps to Reproduce

On a repo with the markdownlint config: file_finding.py file --type bug --title x --summary 'calls `_next_number` then `__main__` runs' --severity Low --steps s --fix f; npx markdownlint the created file -> MD037/MD050 errors.

## Proposed Fix

Backtick-wrap identifier-shaped tokens (contain _ or dunder) in rendered prose fields at write time, or lint the rendered body before writing and warn/refuse with the offending line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
