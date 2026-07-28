# BG0343: file_finding writes Affects from where the evidence was found, not where the fix lands, and never includes a test file

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK); agent; skill v5.0.0

## Summary

`file_finding.py` sets the Affects metadata from the finding's `file` field, which is the location the evidence was READ, not the footprint the unit will CHANGE. Every one of the 54 artefacts filed from the 2026-07-27 audit inherited a single-path Affects on that basis, and not one names a test file, although each fix needs a test under this project's own red-first doctrine. Where evidence and fix coincide the value is right by luck; where they do not it is simply wrong - CR0425's Affects named sdlc-studio/personas/index.md when the change is in artifact.py.

## Steps to Reproduce

1. File any finding whose evidence sits in a different file from its fix. 2. Read the artefact's Affects: it names the evidence file alone. 3. Confirm at scale: all 16 bugs in RUN-01KYHVWK declare one source file and none declares its test file, though `test_validate.py`, `test_verify_ac.py`, `test_transition.py` and the rest all exist. 4. Confirm the harm is the project's own stated harm: refine refuses a fictional footprint because it 'mis-groups the unit in the plan's collision analysis, under-reads it in the engagement floor, and misreports it in gate's changed-surface pass'. An understated footprint causes all three silently, because nothing refuses it. 5. Confirm corpus scale: validate.py reports 191 affects-undeclared warnings.

## Proposed Fix

Treat the finding's evidence location as evidence, not as footprint. Ask the filer for the paths the fix will touch, defaulting to the evidence file only when nothing better is known, and derive the companion test path for a source file whose test exists by convention. At minimum, warn at filing time when a unit that will plainly need a test declares no test file, rather than leaving it for validate to report 191 times.

## Acceptance Criteria

### AC1: a source file declared without its existing test is named

- **Given** a footprint naming `scripts/thing.py`, whose `scripts/tests/test_thing.py` exists
- **When** the filer resolves the declared `Affects`
- **Then** the exact missing test path is returned as an understated-footprint pair
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::CompanionTestFootprintTests::test_missing_companion_test_is_named_by_the_predicate
- **Verified:** yes (2026-07-28)

### AC2: no companion on disk means no invented path

- **Given** a footprint naming a source file with no test file beside it
- **When** the check runs
- **Then** nothing is reported - the tool never sends an author to a file it made up
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::CompanionTestFootprintTests::test_no_companion_on_disk_means_no_invented_path
- **Verified:** yes (2026-07-28)

### AC3: the gap is visible at filing time, not left to validate

- **Given** a bug filed through the CLI with a source-only `Affects`
- **When** the filing completes
- **Then** stderr names the missing test path and the artefact is still written (a warning, never
  a refusal, so the finding in hand is never lost)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::CompanionTestFootprintTests::test_the_cli_reports_the_missing_test_path
- **Verified:** yes (2026-07-28)

### AC4: a complete footprint files silently

- **Given** an `Affects` naming both the source and its test
- **When** the bug is filed
- **Then** stderr is empty - the warning never becomes noise a reader learns to ignore
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::CompanionTestFootprintTests::test_a_complete_footprint_files_silently
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK) | Filed |
| 2026-07-28 | Claude Opus 5 (RUN-01KYJZGZ delivery) | Fixed: the filer names the missing companion test at filing time. The artefact's premise that the code derives `Affects` from a `file` field was falsified - no such field exists; the actionable half (the "at minimum" clause) is what shipped |
