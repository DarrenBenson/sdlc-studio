# BG0399: file_finding discards a CR's steps and fix fields, so BG0384's defect is still live in the other filer

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** CR0498 was filed with steps and fix populated; neither reached the document. Restored by hand 2026-07-29.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`file_finding`'s CR renderer emits Summary, Impact, Acceptance Criteria and Revision History and nothing else. A `steps` or `fix` field supplied for a CR reaches no part of the document, and the command exits 0 reporting the id it minted.

Caught on CR0498 itself: both fields were written at filing, and neither is in the artefact. The whole Proposed Fix - five named remedies with the measurements behind them - was discarded, and only re-reading the document found it.

This is BG0384 exactly, one filer later. That repair gave `artifact.py` a `_land_supplied` pass that appends a section for any supplied field the render has no home for, plus a refusal as a backstop. `file_finding.py` got neither, so the two sanctioned paths to one artefact still disagree about what a supplied field MEANS - which is the pairing LL0016 names and the third time this session it has cost something.

## Steps to Reproduce

1. `file_finding.py file --type cr --fields-file <doc>` with `steps` and `fix` populated.
2. Exit 0, id minted, index row written.
3. `grep -c 'Proposed Fix' <the new file>` -> 0. Neither field is anywhere in the document.

## Proposed Fix

Give `file_finding` the same treatment `artifact.py` received: land a supplied field the renderer has no home for by appending its section before Revision History, and keep a refusal as the backstop for a value that genuinely reaches nothing. Better, have both filers share ONE renderer for the common sections rather than two that drift - the divergence is the defect, and closing this instance without closing the seam leaves the next field to be discovered the same way.

## Acceptance Criteria

- [ ] A CR filed with `steps` and `fix` carries both in its document.
- [ ] A supplied field the renderer has no home for is landed, not dropped, for every type the filer accepts - asserted over the whole type/field matrix rather than one example.
- [ ] The two filers agree: the same fields document filed through `artifact.py new` and through `file_finding.py file` yields the same fields present, asserted as agreement rather than two expected outcomes.
- [ ] CR0498 carries the Steps and Proposed Fix it was filed with.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | Claude Opus 5 | Filed |
