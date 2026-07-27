# BG0343: file_finding writes Affects from where the evidence was found, not where the fix lands, and never includes a test file

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK) | Filed |
