# BG0850: A carried unit's discharge approval is refused by the review cap that another reviewer's rounds filled

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T14:04:42Z

## Summary

Found in a consuming web project's run: a unit carried at the review cap is refused Fixed/Done until the reviewer who rejected it records an APPROVE (transition.py: 'reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id)'). When the re-delivery run's rounds were recorded under a different reviewer id (REJECT then APPROVE, two rounds), `critic.py record` then refuses the rejecting reviewer's APPROVE at the cap ('2 review round(s) recorded, at the cap of 2'), so no path discharges the old REJECT short of --force. Separately, `critic.py record` accepted both rounds from the different reviewer silently, although neither could ever discharge the carry - the operator learnt it only at transition time.

## Steps to Reproduce

1. Carry unit X with two REJECTs from reviewer A.
2. In a new run, record reviewer B: REJECT, then APPROVE.
3. transition X -> Fixed: refused, A's REJECT unanswered.
4. critic record X APPROVE --reviewer A: refused at the cap.

## Proposed Fix

Either let the rejecting reviewer's discharge APPROVE of a carried unit through the cap (it answers an older run's REJECT, not a new round), or have `critic record` warn - at brief and at record - when a carried unit's verdict comes from a reviewer other than the one whose REJECT is outstanding.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Found in a consuming web project's run: a unit carried at the review cap is refused Fixed/Done until the reviewer who rejected it records an APPROVE...
- [ ] **AC2** The proposed fix lands, pinned by a test: Either let the rejecting reviewer's discharge APPROVE of a carried unit through the cap (it answers an older run's REJECT, not a new round), or have `critic...

## Impact

An approved, merged unit cannot reach Fixed without a forced override, and the briefing error that caused it is invisible until the transition.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
