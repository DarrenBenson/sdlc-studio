# BG0297: the two duplicate-detection entry points now share an algorithm but not a scope: file_finding scans every artefact type while artifact new scans only the minted type, so a terminal cross-type duplicate warns on one path and not the other

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Severity:** Low
> **Points:** 2

## Summary

BG0294 unified the duplicate-detection ALGORITHM (both entry points call `artifact.duplicate_candidates)`, but the SCOPE still diverges: `file_finding.duplicate_candidates` loops every `DUP_TYPE`, while artifact.new <type> checks only the minted type. So the same title filed as a bug is compared against CRs/RFCs/epics through the finding filer but only against bugs through artifact new - a terminal cross-type near-match warns on one path and not the other, and comparing a bug to a CR by title is the structural-pairing noise artifact deliberately avoids within a type. No terminal-status set-equality test pins the two paths' agreement.

## Steps to Reproduce

1. A terminal CR shares a title with a bug about to be filed. 2. File the bug via `file_finding.file` - it warns (cross-type scan reaches the CR). 3. Mint the same via artifact.py new --type bug - it does NOT warn (within-type scan only sees bugs). The two entry points disagree.

## Proposed Fix

Make the finding filer scan the finding's OWN type, matching artifact new, so both entry points have identical scope as well as algorithm (a bug is compared to bugs, not to CRs). Add a test asserting both entry points return the SAME candidate ids for a terminal same-type duplicate.

## Acceptance Criteria

### AC1: both entry points agree on a terminal same-type duplicate

- **Given** a terminal (Fixed) bug whose title a new bug filing restates
- **When** the duplicate check runs through the finding filer (scoped to the type) and through artifact new
- **Then** both return the SAME candidate ids, the terminal artefact included
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateScopeParityTests::test_both_entry_points_agree_on_a_terminal_same_type_duplicate
- **Verified:** yes (2026-07-26)

### AC2: the filer no longer warns across types

- **Given** a CR that shares a title with a bug about to be filed, and no matching bug
- **When** the bug is checked through the finding filer (scoped to bugs)
- **Then** the CR is NOT surfaced - matching artifact new bug exactly - while the type-agnostic form still scans every type
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateScopeParityTests::test_the_filer_no_longer_warns_across_types
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
