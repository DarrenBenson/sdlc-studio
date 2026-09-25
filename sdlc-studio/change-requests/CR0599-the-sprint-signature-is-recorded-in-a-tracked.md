# CR-0599: The sprint signature is recorded in a tracked file, so any clone can verify a signed report

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Date:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:05:05Z

## Summary

A signed sprint report is anchored to signature.report and signature.fingerprint in the run record, which lives in gitignored sdlc-studio/.local and exists only in the clone that signed. Anyone who can write that clone's .local can re-point or strip the signature, and any other clone cannot verify the signature at all (`sprint_report` check exits 2 with no run record). Found by BG0775's QA review.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Raised |
