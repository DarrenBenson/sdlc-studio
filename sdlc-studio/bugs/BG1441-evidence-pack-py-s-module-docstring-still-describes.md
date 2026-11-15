# BG1441: evidence_pack.py's module docstring still describes the wider author refusal BG1439 removed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_docstring.py, changelog.d/BGXXXX.md
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1439, qa-seat-BG1439-r1, verdict sdlc-studio/reviews/verdicts/BG1439/be32c29607c3-c0642b0a.txt (non-blocking)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T03:43:06Z

## Summary

After BG1439 the evidence pack refuses a signing principal only when it reads as an agent or is a live author of the report's own units, but the module docstring (scripts/`evidence_pack.py`:17-19) still says it refuses any author recorded in the review ledgers.

## Steps to Reproduce

Read scripts/`evidence_pack.py`'s module docstring beside `unit_authors`.

## Proposed Fix

State the live-author-of-the-report's-own-units rule in the docstring.

## Acceptance Criteria

- [ ] **AC1** Given `evidence_pack.py`'s module docstring, when it states who is refused as accountable, then it names agents and live authors of the report's own units only. Fails on: any wording that refuses every recorded author.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_docstring.py::DocstringTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
