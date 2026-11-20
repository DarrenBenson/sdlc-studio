# BG1665: critic.py record refuses a parallel second seat's verdict once the first seat's REJECT is recorded, so its REJECT never reaches the ledger

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T12:37:01Z

## Summary

In run twenty (RUN-01M7VNR0) US1055's qa and engineering seats reviewed the same delivery (b30aa999) in parallel and both rejected it on the same blocker. lane accept recorded the qa REJECT as round 1; critic.py record then refused the engineering verdict: 'round 2 of US1055 re-checks the fixes to agent-... (qa)'s REJECT, so it must be recorded by agent-... (qa)'. The engineering REJECT stays as an unrecorded file in reviews/verdicts/US1055/, the ledger shows one seat where two judged, and once the qa seat approves the repair at round 2 the engineering seat can judge it only past the cap under an operator ruling. Related to BG1661 (the sequential case).

## Steps to Reproduce

Brief a high-risk unit's qa and engineering seats on the same delivery, have both write a REJECT, record the qa one with lane accept, then record the engineering one with critic.py record --from-verdict: it is refused as a round from the wrong reviewer.

## Proposed Fix

Count verdicts on the same delivery (same diff fingerprint) from different seats as one round, so a parallel second seat's verdict records beside the first; or have the high-risk plan brief the second seat only after the first seat's verdict is recorded.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run twenty (RUN-01M7VNR0) US1055's qa and engineering seats reviewed the same delivery (b30aa999) in parallel and both rejected it on the same blocker.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Brief a high-risk unit's qa and engineering seats on the same delivery, have both write a REJECT, record the qa one with lane accept, then record the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Count verdicts on the same delivery (same diff fingerprint) from different seats as one round, so a parallel second seat's verdict records beside the first; or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
