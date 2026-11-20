# BG1656: The consult's load step never classifies a flat Served card, and BG1535's tests accept the stakeholder declaration anywhere on the card

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_gen.py, tools/tests/test_persona_coherence.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_gen.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:51:21Z

## Summary

BG1535's qa seat (verdict sdlc-studio/reviews/verdicts/BG1535/aef139b4948a-8b25e73a.txt, RUN-01M7VNR0). The consult's step 1 still runs `persona_gen.py` classify (reference-consult.md:271), but `persona_gen._paths` and `provisional_seats` scan only seats/ and stakeholders/ (`persona_gen.py`:104, 119), so the flat Customer or Served card BG1535 admits to the panel is never classified, and a provisional one is not named. `STAKEHOLDER_TYPE` (tools/tests/`test_persona_coherence.py`:1241) matches the declaration anywhere on the card, including quoted inside a code span, and AC1's test accepts the rule anywhere after the Customer / Served marker rather than inside its bullet.

## Steps to Reproduce

Mark a flat persona card provisional and run `persona_gen.py` classify --root .: it is not listed. Replace Graham Doyle's declaration comment with prose quoting it in a code span: ServedHomeTests stays green.

## Proposed Fix

Scan flat cards carrying the served declaration in `persona_gen`'s paths, and anchor both tests to the declaration line and the bullet.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1535's qa seat (verdict sdlc-studio/reviews/verdicts/BG1535/aef139b4948a-8b25e73a.txt, RUN-01M7VNR0).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Mark a flat persona card provisional and run `persona_gen.py` classify --root .: it is not listed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Scan flat cards carrying the served declaration in `persona_gen`'s paths, and anchor both tests to the declaration line and the bullet.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
