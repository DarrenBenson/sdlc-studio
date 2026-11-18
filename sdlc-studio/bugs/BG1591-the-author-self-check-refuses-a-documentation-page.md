# BG1591: The author self-check refuses a documentation page the unit's Affects declares as a claim surface, so a docs unit's claims in its own page cannot be recorded and the land refuses its self-check

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** .local/run17/land-US1321.log (2026-11-18): US1321 landed at 42fc6eb5 and its self-check was refused on claim 27, surface docs/evidence.md.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:00:52Z

## Summary

`check_self_check` (critic.py) accepts claims only on the commit message, the unit's changelog fragments, Resolutions, docstrings, comments and CHANGELOG. A documentation unit makes most of its claims in the page it writes, so a builder that inventories them under that page's path (for example docs/evidence.md) has its whole self-check refused at `sprint lane land`, and the orchestrator has to drop the claim by hand to record it. Met on US1321 in run seventeen; every docs unit in CR0742's run (US1316 to US1320) declares a page.

## Steps to Reproduce

Hand in a self-check whose claims file has one entry with surface "docs/evidence.md" for a unit whose Affects declares docs/evidence.md, then run `sprint lane land`. It commits the unit and prints 'self-check REFUSED ... claim N names the surface 'docs/evidence.md', which the self-check does not name'.

## Proposed Fix

Accept as a claim surface any markdown page the unit's Affects declares (optional, like docstrings), and name it in the lane brief's claim-inventory list, so a docs unit inventories its page's claims under the page's path.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `check_self_check` (critic.py) accepts claims only on the commit message, the unit's changelog fragments, Resolutions, docstrings, comments and CHANGELOG.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Hand in a self-check whose claims file has one entry with surface "docs/evidence.md" for a unit whose Affects declares docs/evidence.md, then run `sprint lane...
- [ ] **AC3** The proposed fix lands, pinned by a test: Accept as a claim surface any markdown page the unit's Affects declares (optional, like docstrings), and name it in the lane brief's claim-inventory list, so a...

## Impact

A docs unit's own page, where its claims live, is the one surface the inventory cannot carry, so either the claims go unrecorded or the land's self-check is refused and recorded by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
