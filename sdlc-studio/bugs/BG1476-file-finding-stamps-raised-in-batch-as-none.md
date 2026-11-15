# BG1476: file_finding stamps Raised-in-batch as none open for a finding filed while a run is open

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1476.md
> **Evidence:** sdlc-studio/bugs/BG1455 to BG1473, filed during RUN-01M7EYR3.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:40:28Z

## Summary

Every finding filed during run thirteen (BG1455 to BG1473, while RUN-01M7EYR3 was open) carries `Raised-in-batch: none open - raised outside a delivery batch, <time>`. The stamp never names the run a finding was raised in, so a reader cannot tell which run's work surfaced it; the close dates findings by the timestamp alone.

## Steps to Reproduce

1. Open a run with `sprint.py plan --write`.
2. File a bug with `file_finding.py file`.
3. Read its Raised-in-batch line: 'none open'.

## Proposed Fix

Stamp the open run's id when a run is open, falling back to 'none open' only when no run is.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Every finding filed during run thirteen (BG1455 to BG1473, while RUN-01M7EYR3 was open) carries `Raised-in-batch: none open - raised outside a delivery batch...
- [ ] **AC2** The proposed fix lands, pinned by a test: Stamp the open run's id when a run is open, falling back to 'none open' only when no run is.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
