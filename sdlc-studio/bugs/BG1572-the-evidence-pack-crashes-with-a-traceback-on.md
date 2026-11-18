# BG1572: The evidence pack crashes with a traceback on a malformed report instead of refusing it by name

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py
> **Evidence:** BG1524 QA verdict, sdlc-studio/reviews/verdicts/BG1524/bda4e4dce0f6-603dbf96.txt
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T00:23:09Z

## Summary

The QA review of BG1524 (run sixteen, APPROVE) found that a report the signature check cannot parse raises an uncaught exception, so the pack build stops with a Python traceback and writes nothing. A refusal naming the report and what is malformed is what every other check in the pack does.

## Steps to Reproduce

Build the evidence pack over a tree holding one report whose signature block is truncated.

## Proposed Fix

Catch the parse failure per report and refuse naming the report and the field.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA review of BG1524 (run sixteen, APPROVE) found that a report the signature check cannot parse raises an uncaught exception, so the pack build stops with...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Build the evidence pack over a tree holding one report whose signature block is truncated.
- [ ] **AC3** The proposed fix lands, pinned by a test: Catch the parse failure per report and refuse naming the report and the field.

## Impact

An operator building the pack sees a traceback rather than which report to fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
