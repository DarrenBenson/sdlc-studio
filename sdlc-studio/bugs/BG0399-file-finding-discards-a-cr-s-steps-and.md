# BG0399: file_finding discards a CR's steps and fix fields, so BG0384's defect is still live in the other filer

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
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

### AC1: a CR's steps and fix reach the document

- **Given** a change request filed with `steps` and `fix` supplied
- **When** it is filed
- **Then** both appear in the filed document under their own sections, rather than being discarded without a word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::NoSuppliedFieldIsDiscardedTests::test_a_crs_steps_and_fix_reach_the_document
- **Verified:** yes (2026-07-29)

### AC2: the rule is derived over every type and every field

- **Given** each of the three renderers and each landable prose field
- **When** it is filed
- **Then** every field reaches its section, so a renderer added later is covered without anyone remembering to add a case - the omission this bug is about was one renderer nobody re-read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::NoSuppliedFieldIsDiscardedTests::test_every_landable_field_reaches_every_type
- **Verified:** yes (2026-07-29)

### AC3: a field the type already homes is not duplicated

- **Given** a bug, whose renderer already emits Steps and Fix
- **When** it is filed
- **Then** each section appears exactly once, so the lander repairs the gap without doubling what worked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::NoSuppliedFieldIsDiscardedTests::test_a_field_the_type_already_homes_is_not_duplicated
- **Verified:** yes (2026-07-29)

### AC4: an unsupplied field adds no empty section

- **Given** a change request filed with neither steps nor fix
- **When** it is filed
- **Then** no empty section is added, so the document is not padded with headings nobody wrote under
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::NoSuppliedFieldIsDiscardedTests::test_an_unsupplied_field_adds_no_empty_section
- **Verified:** yes (2026-07-29)

### AC5: a landed section keeps the document's shape

- **Given** a landed section
- **When** it is filed
- **Then** it precedes the revision history, so every consumer that reads to the history is unaffected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::NoSuppliedFieldIsDiscardedTests::test_a_landed_section_precedes_the_revision_history
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | Claude Opus 5 | Filed |
