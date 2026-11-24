# BG1559: The skill maintainer persona card states two Frustrations as current that were fixed weeks ago

> **Status:** Won't Fix
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

- [ ] **AC1** Given the Frustrations section of the skill maintainer persona card, when the test resolves every Bug or CR id a bullet cites, then no bullet states as current a condition whose cited id is at a terminal status: the BG1065 and BG1054 bullets are replaced by frustrations that still hold or are marked as resolved history in the past tense. Fails on: a present-tense frustration citing a Fixed bug.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::FrustrationsCurrencyTests::test_no_current_frustration_cites_a_terminal_id
- [ ] **AC2** Given a fixture card with one bullet citing a Fixed bug unmarked, one citing a Fixed bug marked as resolved history and one citing an Open bug, when the same check runs, then only the unmarked bullet is reported. Fails on: a check that reports every cited id, or one that passes the stale bullet.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::FrustrationsCurrencyTests::test_a_stale_bullet_is_reported_and_an_open_or_marked_one_passes

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because it lies in this repository's own CI, hooks or tools, which the installed skill does not ship. This repository's own persona card.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
