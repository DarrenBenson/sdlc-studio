# BG1092: The TSD says the commit-msg hook falls back to skill-tests.sh only without pytest; it also does when the handover carries no selectors

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_tsd_noise_ratchet_place.py, changelog.d/BG1092.md
> **Evidence:** US1084 QA review, round 2 (APPROVE), qa-seat-US1084-r1, 2026-10-19, at 69c8c210: [new] item 4, .githooks/commit-msg:274.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T19:12:47Z

## Summary

US1084 rewrote the TSD's noise-ratchet paragraph (tsd.md:205-210) and its changelog to say the commit-msg hook runs tools/skill-tests.sh, ratchet included, only on a machine without pytest. .githooks/commit-msg:274 takes the pytest path only when the handover carries selectors, so a commit whose suite decision is 'run everything' (no selector line) also falls back to skill-tests.sh with pytest installed.

## Steps to Reproduce

`GIT_DIR=/nonexistent python3 .claude/skills/sdlc-studio/scripts/gate.py --suite-decision --staged` prints 'suite-decision: run ... running everything', 'suite-mode: full' and no selector line; commit-msg then takes the skill-tests.sh branch.

## Proposed Fix

Say both conditions: no pytest, or no selection.

## Acceptance Criteria

- [ ] **AC1** The TSD names both conditions under which the commit-msg hook runs tools/skill-tests.sh
  - **Verify:** pytest tools/tests/test_tsd_noise_ratchet_place.py::NoiseRatchetPlaceTests

## Impact

A reader is told the ratchet never runs at commit where pytest is installed, when it does on a full-run commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
