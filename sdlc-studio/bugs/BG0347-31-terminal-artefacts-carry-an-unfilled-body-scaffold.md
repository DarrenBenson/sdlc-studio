# BG0347: 31 terminal artefacts carry an unfilled body scaffold, including 12 bugs with no symptom, steps or fix

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 5
> **Affects:** sdlc-studio/.placeholder-baseline.txt, sdlc-studio/bugs, sdlc-studio/epics, sdlc-studio/change-requests
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (revealed by BG0304's widened sweep during RUN-01KYHVWK); agent; skill v5.0.0

## Summary

BG0304 widened the placeholder sweep from the acceptance-criteria section to the whole body, and the widened check immediately found 62 findings across 31 already-terminal artefacts that the narrow check had never looked at: 12 bugs still carrying the raw {{symptom}}, {{steps}} and {{fix}} scaffolds, 11 epics whose Summary is {{what this epic groups}}, and 7 change requests with {{what changes and why}} and {{who this affects and what breaks}} unfilled. These are finished records with blanks where their content should be - a closed bug that never said what went wrong is indistinguishable from one nobody investigated.

## Steps to Reproduce

1. Run validate.py check: 0 errors, and 62 placeholder findings downgraded to warnings by the baseline. 2. Read sdlc-studio/.placeholder-baseline.txt - the 31 ids, captured from the checker's own output rather than by hand. 3. Open any listed bug: its Summary, Steps to Reproduce and Proposed Fix are template placeholders.

## Proposed Fix

Backfill each artefact's missing content and remove its id from the baseline. Removal is one-way by design: once an id leaves the list the check errors on it, so the count can only fall. Where a record's content is genuinely unrecoverable - nobody remembers what the bug was - say so explicitly in the artefact rather than leaving a scaffold, and remove it from the baseline on that basis.

## Acceptance Criteria

### AC1: no terminal artefact carries an unfilled body scaffold

- **Given** the workspace
- **When** it is read
- **Then** `validate check` reports no unresolved body placeholder - a closed bug that never said what went wrong is indistinguishable from one nobody investigated
- **Verify:** shell test $(python3 .claude/skills/sdlc-studio/scripts/validate.py check 2>&1 | grep -c 'unresolved placeholder in body') -eq 0
- **Verified:** yes (2026-07-29)

### AC2: the absence is STATED, never reconstructed

- **Given** a field that was never filled at the time
- **When** it is read
- **Then** the record says so and points at what does carry its substance, because inventing what an author would have said is the false-evidence class this project files bugs about
- **Verify:** shell grep -q 'Not recorded at the time' sdlc-studio/bugs/BG0271-the-site-sweep-test-is-unrunnable-inside-a.md
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (revealed by BG0304's widened sweep during RUN-01KYHVWK) | Filed |
