# BG1047: test_status's backlog advisory fixture dates its bugs 2026-07-16, so it went stale on 2026-10-14 and main is red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_status.py, changelog.d/BG1047.md
> **Evidence:** devserver1 push gate for BG1044's tree 5e0ecf4c on 2026-10-14: [FAIL] full-suite, 1 red, test_status.py::BacklogTriageAdvisoryTests::test_silent_on_a_coherent_backlog; reproduced locally in 0.18s.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T11:11:19Z

## Summary

`BacklogTriageAdvisoryTests._bug` in scripts/tests/`test_status.py` writes each fixture bug with '> **Date:** 2026-07-16', while `status.backlog_triage_advisory` reads staleness against the real clock (`backlog_triage.triage`, `stale_days`=90). On 2026-10-14, day 90, both fixture bugs read stale, so `test_silent_on_a_coherent_backlog` fails on every machine and every tree: the devserver1 push gate went red on it for BG1044 (1 failed, 8124 passed) with no change near status.py. `test_backlog_triage.py` is not affected: it pins today to `MEASURED_TODAY.`

## Steps to Reproduce

On or after 2026-10-14, run pytest .claude/skills/sdlc-studio/scripts/tests/`test_status.py`::BacklogTriageAdvisoryTests::`test_silent_on_a_coherent_backlog`: 'backlog triage: 2 item(s) - 2 stale' is not None.

## Proposed Fix

Date the fixture's bugs today, so the coherent backlog stays coherent whatever the date and the duplicate-pair test still fires on its duplicates.

## Acceptance Criteria

- [ ] **AC1** Given today's date, when `test_status.py`'s backlog advisory tests run, then a coherent backlog reads silent and a duplicate pair still fires.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BacklogTriageAdvisoryTests
  - **Verified:** yes (2026-10-14)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
