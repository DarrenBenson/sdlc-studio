# BG1559: The skill maintainer persona card states two Frustrations as current that were fixed weeks ago

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, tools/tests/test_persona_coherence.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at sdlc-studio/personas/rowan-achterberg-skill-maintainer.md ## Frustrations, bullets 2 and 5
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:19Z

## Summary

The Frustrations section of the skill maintainer persona card describes what trips the persona up with the current tools, and a unit on the repository-tooling interface is judged against this card. Two of its six bullets describe conditions in the present tense that the bugs they cite record as Fixed: the gate's 45-second cost budget being exceeded on every run (BG1065) and a scheduled CI job left red for weeks (BG1054). The card was last dated after both fixes. The Primary's card for that interface therefore argues for work already done. The persona coherence test only checks that a cited id resolves, not that it is still open, so the staleness passes unnoticed.

## Steps to Reproduce

1. Open sdlc-studio/personas/rowan-achterberg-skill-maintainer.md and read the Frustrations section.
2. Read the bullet ending at line 59, which says the gate's cost budget is exceeded on every run and cites BG1065.
3. Read the bullet at line 63, which says a scheduled CI job has been red for weeks and cites BG1054.
4. Open the BG1065 and BG1054 files under sdlc-studio/bugs/ and read the Status line of each: both are Fixed.
5. Run validate.py with the personas verb: it reports the personas as well-formed.

## Proposed Fix

Rewrite the two bullets so the card states what is true now: either replace each with a frustration that still holds, or keep the history in the past tense as a resolved example and say so. Extend tools/tests/`test_persona_coherence.py` so a Frustrations bullet that cites a Bug or CR at a terminal status fails unless the bullet is marked as resolved history, with a positive control showing a bullet citing an open id passes.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The Frustrations section of the skill maintainer persona card describes what trips the persona up with the current tools, and a unit on the repository-tooling...
- [ ] **AC2** The proposed fix lands, pinned by a test: Rewrite the two bullets so the card states what is true now: either replace each with a frustration that still holds, or keep the history in the past tense as...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
